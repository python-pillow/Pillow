from __future__ import annotations

import gc
import os
import re
import warnings
import xml.etree.ElementTree
from contextlib import contextmanager
from io import BytesIO
from struct import unpack

import pytest

from PIL import AvifImagePlugin, Image, ImageDraw, UnidentifiedImageError, features

from .helper import (
    PillowLeakTestCase,
    assert_image,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

try:
    from PIL import _avif

    HAVE_AVIF = True
except ImportError:
    HAVE_AVIF = False


TEST_AVIF_FILE = "Tests/images/avif/hopper.avif"


def assert_xmp_orientation(xmp, expected):
    assert isinstance(xmp, bytes)
    root = xml.etree.ElementTree.fromstring(xmp)
    orientation = None
    for elem in root.iter():
        if elem.tag.endswith("}Description"):
            orientation = elem.attrib.get("{http://ns.adobe.com/tiff/1.0/}Orientation")
            if orientation:
                orientation = int(orientation)
                break
    assert orientation == expected


def roundtrip(im, **options):
    out = BytesIO()
    im.save(out, "AVIF", **options)
    out.seek(0)
    return Image.open(out)


def skip_unless_avif_decoder(codec_name):
    reason = f"{codec_name} decode not available"
    return pytest.mark.skipif(
        not HAVE_AVIF or not _avif.decoder_codec_available(codec_name), reason=reason
    )


def skip_unless_avif_encoder(codec_name):
    reason = f"{codec_name} encode not available"
    return pytest.mark.skipif(
        not HAVE_AVIF or not _avif.encoder_codec_available(codec_name), reason=reason
    )


def is_docker_qemu():
    try:
        init_proc_exe = os.readlink("/proc/1/exe")
    except:  # noqa: E722
        return False
    else:
        return "qemu" in init_proc_exe


def has_alpha_premultiplied(im_bytes):
    stream = BytesIO(im_bytes)
    length = len(im_bytes)
    while stream.tell() < length:
        start = stream.tell()
        size, boxtype = unpack(">L4s", stream.read(8))
        if not all(0x20 <= c <= 0x7E for c in boxtype):
            # Not ascii
            return False
        if size == 1:  # 64bit size
            (size,) = unpack(">Q", stream.read(8))
        end = start + size
        version, _ = unpack(">B3s", stream.read(4))
        if boxtype in (b"ftyp", b"hdlr", b"pitm", b"iloc", b"iinf"):
            # Skip these boxes
            stream.seek(end)
            continue
        elif boxtype == b"meta":
            # Container box possibly including iref prem, continue to parse boxes
            # inside it
            continue
        elif boxtype == b"iref":
            while stream.tell() < end:
                _, iref_type = unpack(">L4s", stream.read(8))
                version, _ = unpack(">B3s", stream.read(4))
                if iref_type == b"prem":
                    return True
                stream.read(2 if version == 0 else 4)
        else:
            return False
    return False


class TestUnsupportedAvif:
    def test_unsupported(self, monkeypatch):
        monkeypatch.setattr(AvifImagePlugin, "SUPPORTED", False)

        file_path = "Tests/images/avif/hopper.avif"
        pytest.warns(
            UserWarning,
            lambda: pytest.raises(UnidentifiedImageError, Image.open, file_path),
        )

    def test_unsupported_open(self, monkeypatch):
        monkeypatch.setattr(AvifImagePlugin, "SUPPORTED", False)

        file_path = "Tests/images/avif/hopper.avif"
        with pytest.raises(SyntaxError):
            AvifImagePlugin.AvifImageFile(file_path)


@skip_unless_feature("avif")
class TestFileAvif:
    def test_version(self):
        _avif.AvifCodecVersions()
        assert re.search(r"\d+\.\d+\.\d+$", features.version_module("avif"))

    def test_read(self):
        """
        Can we read an AVIF file without error?
        Does it have the bits we expect?
        """

        with Image.open("Tests/images/avif/hopper.avif") as image:
            assert image.mode == "RGB"
            assert image.size == (128, 128)
            assert image.format == "AVIF"
            assert image.get_format_mimetype() == "image/avif"
            image.load()
            image.getdata()

            # generated with:
            # avifdec hopper.avif hopper_avif_write.png
            assert_image_similar_tofile(
                image, "Tests/images/avif/hopper_avif_write.png", 12.0
            )

    def _roundtrip(self, tmp_path, mode, epsilon, args={}):
        temp_file = str(tmp_path / "temp.avif")

        hopper(mode).save(temp_file, **args)
        with Image.open(temp_file) as image:
            assert image.mode == "RGB"
            assert image.size == (128, 128)
            assert image.format == "AVIF"
            image.load()
            image.getdata()

            if mode == "RGB":
                # avifdec hopper.avif avif/hopper_avif_write.png
                assert_image_similar_tofile(
                    image, "Tests/images/avif/hopper_avif_write.png", 12.0
                )

            # This test asserts that the images are similar. If the average pixel
            # difference between the two images is less than the epsilon value,
            # then we're going to accept that it's a reasonable lossy version of
            # the image.
            target = hopper(mode)
            if mode != "RGB":
                target = target.convert("RGB")
            assert_image_similar(image, target, epsilon)

    def test_write_rgb(self, tmp_path):
        """
        Can we write a RGB mode file to avif without error?
        Does it have the bits we expect?
        """

        self._roundtrip(tmp_path, "RGB", 12.5)

    def test_AvifEncoder_with_invalid_args(self):
        """
        Calling encoder functions with no arguments should result in an error.
        """
        with pytest.raises(TypeError):
            _avif.AvifEncoder()

    def test_AvifDecoder_with_invalid_args(self):
        """
        Calling decoder functions with no arguments should result in an error.
        """
        with pytest.raises(TypeError):
            _avif.AvifDecoder()

    def test_encoder_finish_none_error(self, monkeypatch, tmp_path):
        """Save should raise an OSError if AvifEncoder.finish returns None"""

        class _mock_avif:
            class AvifEncoder:
                def __init__(self, *args, **kwargs):
                    pass

                def add(self, *args, **kwargs):
                    pass

                def finish(self):
                    return None

        monkeypatch.setattr(AvifImagePlugin, "_avif", _mock_avif)

        im = Image.new("RGB", (150, 150))
        test_file = str(tmp_path / "temp.avif")
        with pytest.raises(OSError):
            im.save(test_file)

    def test_no_resource_warning(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as image:
            temp_file = str(tmp_path / "temp.avif")
            with warnings.catch_warnings():
                image.save(temp_file)

    @pytest.mark.parametrize("major_brand", [b"avif", b"avis", b"mif1", b"msf1"])
    def test_accept_ftyp_brands(self, major_brand):
        data = b"\x00\x00\x00\x1cftyp%s\x00\x00\x00\x00" % major_brand
        assert AvifImagePlugin._accept(data) is True

    def test_file_pointer_could_be_reused(self):
        with open(TEST_AVIF_FILE, "rb") as blob:
            with Image.open(blob) as im:
                im.load()
            with Image.open(blob) as im:
                im.load()

    def test_background_from_gif(self, tmp_path):
        with Image.open("Tests/images/chi.gif") as im:
            original_value = im.convert("RGB").getpixel((1, 1))

            # Save as AVIF
            out_avif = str(tmp_path / "temp.avif")
            im.save(out_avif, save_all=True)

        # Save as GIF
        out_gif = str(tmp_path / "temp.gif")
        with Image.open(out_avif) as im:
            im.save(out_gif)

        with Image.open(out_gif) as reread:
            reread_value = reread.convert("RGB").getpixel((1, 1))
        difference = sum(
            [abs(original_value[i] - reread_value[i]) for i in range(0, 3)]
        )
        assert difference < 5

    def test_save_single_frame(self, tmp_path):
        temp_file = str(tmp_path / "temp.avif")
        with Image.open("Tests/images/chi.gif") as im:
            im.save(temp_file)
        with Image.open(temp_file) as im:
            assert im.n_frames == 1

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        with pytest.raises(SyntaxError):
            AvifImagePlugin.AvifImageFile(invalid_file)

    def test_load_transparent_rgb(self):
        test_file = "Tests/images/avif/transparency.avif"
        with Image.open(test_file) as im:
            assert_image(im, "RGBA", (64, 64))

            # image has 876 transparent pixels
            assert im.getchannel("A").getcolors()[0][0] == 876

    def test_save_transparent(self, tmp_path):
        im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        assert im.getcolors() == [(100, (0, 0, 0, 0))]

        test_file = str(tmp_path / "temp.avif")
        im.save(test_file)

        # check if saved image contains same transparency
        with Image.open(test_file) as im:
            assert_image(im, "RGBA", (10, 10))
            assert im.getcolors() == [(100, (0, 0, 0, 0))]

    def test_save_icc_profile(self):
        with Image.open("Tests/images/avif/icc_profile_none.avif") as im:
            assert im.info.get("icc_profile") is None

            with Image.open("Tests/images/avif/icc_profile.avif") as with_icc:
                expected_icc = with_icc.info.get("icc_profile")
                assert expected_icc is not None

                im = roundtrip(im, icc_profile=expected_icc)
                assert im.info["icc_profile"] == expected_icc

    def test_discard_icc_profile(self):
        with Image.open("Tests/images/avif/icc_profile.avif") as im:
            im = roundtrip(im, icc_profile=None)
        assert "icc_profile" not in im.info

    def test_roundtrip_icc_profile(self):
        with Image.open("Tests/images/avif/icc_profile.avif") as im:
            expected_icc = im.info["icc_profile"]

            im = roundtrip(im)
        assert im.info["icc_profile"] == expected_icc

    def test_roundtrip_no_icc_profile(self):
        with Image.open("Tests/images/avif/icc_profile_none.avif") as im:
            assert im.info.get("icc_profile") is None

            im = roundtrip(im)
        assert "icc_profile" not in im.info

    def test_exif(self):
        # With an EXIF chunk
        with Image.open("Tests/images/avif/exif.avif") as im:
            exif = im.getexif()
        assert exif[274] == 1

    def test_exif_save(self, tmp_path):
        with Image.open("Tests/images/avif/exif.avif") as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            exif = reloaded.getexif()
        assert exif[274] == 1

    def test_exif_obj_argument(self, tmp_path):
        exif = Image.Exif()
        exif[274] = 1
        exif_data = exif.tobytes()
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file, exif=exif)

        with Image.open(test_file) as reloaded:
            assert reloaded.info["exif"] == exif_data

    def test_exif_bytes_argument(self, tmp_path):
        exif = Image.Exif()
        exif[274] = 1
        exif_data = exif.tobytes()
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file, exif=exif_data)

        with Image.open(test_file) as reloaded:
            assert reloaded.info["exif"] == exif_data

    def test_exif_invalid(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            with pytest.raises(ValueError):
                im.save(test_file, exif=b"invalid")

    def test_xmp(self):
        with Image.open("Tests/images/avif/xmp_tags_orientation.avif") as im:
            xmp = im.info.get("xmp")
        assert_xmp_orientation(xmp, 3)

    def test_xmp_save(self, tmp_path):
        with Image.open("Tests/images/avif/xmp_tags_orientation.avif") as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            xmp = reloaded.info.get("xmp")
        assert_xmp_orientation(xmp, 3)

    def test_xmp_save_from_png(self, tmp_path):
        with Image.open("Tests/images/xmp_tags_orientation.png") as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file)

        with Image.open(test_file) as reloaded:
            xmp = reloaded.info.get("xmp")
        assert_xmp_orientation(xmp, 3)

    def test_xmp_save_argument(self, tmp_path):
        xmp_arg = "\n".join(
            [
                '<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>',
                '<x:xmpmeta xmlns:x="adobe:ns:meta/">',
                ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">',
                '  <rdf:Description rdf:about=""',
                '    xmlns:tiff="http://ns.adobe.com/tiff/1.0/"',
                '   tiff:Orientation="1"/>',
                " </rdf:RDF>",
                "</x:xmpmeta>",
                '<?xpacket end="r"?>',
            ]
        )
        with Image.open("Tests/images/avif/hopper.avif") as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file, xmp=xmp_arg)

        with Image.open(test_file) as reloaded:
            xmp = reloaded.info.get("xmp")
        assert_xmp_orientation(xmp, 1)

    def test_tell(self):
        with Image.open(TEST_AVIF_FILE) as im:
            assert im.tell() == 0

    def test_seek(self):
        with Image.open(TEST_AVIF_FILE) as im:
            im.seek(0)

            with pytest.raises(EOFError):
                im.seek(1)

    @pytest.mark.parametrize("subsampling", ["4:4:4", "4:2:2", "4:0:0"])
    def test_encoder_subsampling(self, tmp_path, subsampling):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file, subsampling=subsampling)

    def test_encoder_subsampling_invalid(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            with pytest.raises(ValueError):
                im.save(test_file, subsampling="foo")

    def test_encoder_range(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file, range="limited")

    def test_encoder_range_invalid(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            with pytest.raises(ValueError):
                im.save(test_file, range="foo")

    @skip_unless_avif_encoder("aom")
    @skip_unless_feature("avif")
    def test_encoder_codec_param(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            im.save(test_file, codec="aom")

    def test_encoder_codec_invalid(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            with pytest.raises(ValueError):
                im.save(test_file, codec="foo")

    @skip_unless_avif_decoder("dav1d")
    @skip_unless_feature("avif")
    def test_encoder_codec_cannot_encode(self, tmp_path):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            with pytest.raises(ValueError):
                im.save(test_file, codec="dav1d")

    @skip_unless_avif_encoder("aom")
    @skip_unless_feature("avif")
    def test_encoder_advanced_codec_options(self):
        with Image.open(TEST_AVIF_FILE) as im:
            ctrl_buf = BytesIO()
            im.save(ctrl_buf, "AVIF", codec="aom")
            test_buf = BytesIO()
            im.save(
                test_buf,
                "AVIF",
                codec="aom",
                advanced={
                    "aq-mode": "1",
                    "enable-chroma-deltaq": "1",
                },
            )
            assert ctrl_buf.getvalue() != test_buf.getvalue()

    @skip_unless_avif_encoder("aom")
    @skip_unless_feature("avif")
    @pytest.mark.parametrize("val", [{"foo": "bar"}, 1234])
    def test_encoder_advanced_codec_options_invalid(self, tmp_path, val):
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = str(tmp_path / "temp.avif")
            with pytest.raises(ValueError):
                im.save(test_file, codec="aom", advanced=val)

    @skip_unless_avif_decoder("aom")
    @skip_unless_feature("avif")
    def test_decoder_codec_param(self):
        AvifImagePlugin.DECODE_CODEC_CHOICE = "aom"
        try:
            with Image.open(TEST_AVIF_FILE) as im:
                assert im.size == (128, 128)
        finally:
            AvifImagePlugin.DECODE_CODEC_CHOICE = "auto"

    @skip_unless_avif_encoder("rav1e")
    @skip_unless_feature("avif")
    def test_decoder_codec_cannot_decode(self, tmp_path):
        AvifImagePlugin.DECODE_CODEC_CHOICE = "rav1e"
        try:
            with pytest.raises(ValueError):
                with Image.open(TEST_AVIF_FILE):
                    pass
        finally:
            AvifImagePlugin.DECODE_CODEC_CHOICE = "auto"

    def test_decoder_codec_invalid(self):
        AvifImagePlugin.DECODE_CODEC_CHOICE = "foo"
        try:
            with pytest.raises(ValueError):
                with Image.open(TEST_AVIF_FILE):
                    pass
        finally:
            AvifImagePlugin.DECODE_CODEC_CHOICE = "auto"

    @skip_unless_avif_encoder("aom")
    @skip_unless_feature("avif")
    def test_encoder_codec_available(self):
        assert _avif.encoder_codec_available("aom") is True

    def test_encoder_codec_available_bad_params(self):
        with pytest.raises(TypeError):
            _avif.encoder_codec_available()

    @skip_unless_avif_decoder("dav1d")
    @skip_unless_feature("avif")
    def test_encoder_codec_available_cannot_decode(self):
        assert _avif.encoder_codec_available("dav1d") is False

    def test_encoder_codec_available_invalid(self):
        assert _avif.encoder_codec_available("foo") is False

    def test_encoder_quality_valueerror(self, tmp_path):
        with Image.open("Tests/images/avif/hopper.avif") as im:
            test_file = str(tmp_path / "temp.avif")
            with pytest.raises(ValueError):
                im.save(test_file, quality="invalid")

    @skip_unless_avif_decoder("aom")
    @skip_unless_feature("avif")
    def test_decoder_codec_available(self):
        assert _avif.decoder_codec_available("aom") is True

    def test_decoder_codec_available_bad_params(self):
        with pytest.raises(TypeError):
            _avif.decoder_codec_available()

    @skip_unless_avif_encoder("rav1e")
    @skip_unless_feature("avif")
    def test_decoder_codec_available_cannot_decode(self):
        assert _avif.decoder_codec_available("rav1e") is False

    def test_decoder_codec_available_invalid(self):
        assert _avif.decoder_codec_available("foo") is False

    @pytest.mark.parametrize("upsampling", ["fastest", "best", "nearest", "bilinear"])
    def test_decoder_upsampling(self, upsampling):
        AvifImagePlugin.CHROMA_UPSAMPLING = upsampling
        try:
            with Image.open(TEST_AVIF_FILE):
                pass
        finally:
            AvifImagePlugin.CHROMA_UPSAMPLING = "auto"

    def test_decoder_upsampling_invalid(self):
        AvifImagePlugin.CHROMA_UPSAMPLING = "foo"
        try:
            with pytest.raises(ValueError):
                with Image.open(TEST_AVIF_FILE):
                    pass
        finally:
            AvifImagePlugin.CHROMA_UPSAMPLING = "auto"

    def test_p_mode_transparency(self):
        im = Image.new("P", size=(64, 64))
        draw = ImageDraw.Draw(im)
        draw.rectangle(xy=[(0, 0), (32, 32)], fill=255)
        draw.rectangle(xy=[(32, 32), (64, 64)], fill=255)

        buf_png = BytesIO()
        im.save(buf_png, format="PNG", transparency=0)
        im_png = Image.open(buf_png)
        buf_out = BytesIO()
        im_png.save(buf_out, format="AVIF", quality=100)

        assert_image_similar(im_png.convert("RGBA"), Image.open(buf_out), 1)

    def test_decoder_strict_flags(self):
        # This would fail if full avif strictFlags were enabled
        with Image.open("Tests/images/avif/chimera-missing-pixi.avif") as im:
            assert im.size == (480, 270)

    @skip_unless_avif_encoder("aom")
    def test_aom_optimizations(self):
        im = hopper("RGB")
        buf = BytesIO()
        im.save(buf, format="AVIF", codec="aom", speed=1)

    @skip_unless_avif_encoder("svt")
    def test_svt_optimizations(self):
        im = hopper("RGB")
        buf = BytesIO()
        im.save(buf, format="AVIF", codec="svt", speed=1)


@skip_unless_feature("avif")
class TestAvifAnimation:
    @contextmanager
    def star_frames(self):
        with Image.open("Tests/images/avif/star.png") as f1:
            with Image.open("Tests/images/avif/star90.png") as f2:
                with Image.open("Tests/images/avif/star180.png") as f3:
                    with Image.open("Tests/images/avif/star270.png") as f4:
                        yield [f1, f2, f3, f4]

    def test_n_frames(self):
        """
        Ensure that AVIF format sets n_frames and is_animated attributes
        correctly.
        """

        with Image.open("Tests/images/avif/hopper.avif") as im:
            assert im.n_frames == 1
            assert not im.is_animated

        with Image.open("Tests/images/avif/star.avifs") as im:
            assert im.n_frames == 5
            assert im.is_animated

    def test_write_animation_L(self, tmp_path):
        """
        Convert an animated GIF to animated AVIF, then compare the frame
        count, and first and last frames to ensure they're visually similar.
        """

        with Image.open("Tests/images/avif/star.gif") as orig:
            assert orig.n_frames > 1

            temp_file = str(tmp_path / "temp.avif")
            orig.save(temp_file, save_all=True)
            with Image.open(temp_file) as im:
                assert im.n_frames == orig.n_frames

                # Compare first and second-to-last frames to the original animated GIF
                orig.load()
                im.load()
                assert_image_similar(im.convert("RGB"), orig.convert("RGB"), 25.0)
                orig.seek(orig.n_frames - 2)
                im.seek(im.n_frames - 2)
                orig.load()
                im.load()
                assert_image_similar(im.convert("RGB"), orig.convert("RGB"), 25.0)

    def test_write_animation_RGB(self, tmp_path):
        """
        Write an animated AVIF from RGB frames, and ensure the frames
        are visually similar to the originals.
        """

        def check(temp_file):
            with Image.open(temp_file) as im:
                assert im.n_frames == 4

                # Compare first frame to original
                im.load()
                assert_image_similar(im, frame1.convert("RGBA"), 25.0)

                # Compare second frame to original
                im.seek(1)
                im.load()
                assert_image_similar(im, frame2.convert("RGBA"), 25.0)

        with self.star_frames() as frames:
            frame1 = frames[0]
            frame2 = frames[1]
            temp_file1 = str(tmp_path / "temp.avif")
            frames[0].copy().save(temp_file1, save_all=True, append_images=frames[1:])
            check(temp_file1)

            # Tests appending using a generator
            def imGenerator(ims):
                yield from ims

            temp_file2 = str(tmp_path / "temp_generator.avif")
            frames[0].copy().save(
                temp_file2,
                save_all=True,
                append_images=imGenerator(frames[1:]),
            )
            check(temp_file2)

    def test_sequence_dimension_mismatch_check(self, tmp_path):
        temp_file = str(tmp_path / "temp.avif")
        frame1 = Image.new("RGB", (100, 100))
        frame2 = Image.new("RGB", (150, 150))
        with pytest.raises(ValueError):
            frame1.save(temp_file, save_all=True, append_images=[frame2], duration=100)

    def test_heif_raises_unidentified_image_error(self):
        with pytest.raises(UnidentifiedImageError):
            with Image.open("Tests/images/avif/rgba10.heif"):
                pass

    @pytest.mark.parametrize("alpha_premultipled", [False, True])
    def test_alpha_premultiplied_true(self, alpha_premultipled):
        im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        im_buf = BytesIO()
        im.save(im_buf, "AVIF", alpha_premultiplied=alpha_premultipled)
        im_bytes = im_buf.getvalue()
        assert has_alpha_premultiplied(im_bytes) is alpha_premultipled

    def test_timestamp_and_duration(self, tmp_path):
        """
        Try passing a list of durations, and make sure the encoded
        timestamps and durations are correct.
        """

        durations = [1, 10, 20, 30, 40]
        temp_file = str(tmp_path / "temp.avif")
        with self.star_frames() as frames:
            frames[0].save(
                temp_file,
                save_all=True,
                append_images=(frames[1:] + [frames[0]]),
                duration=durations,
            )

        with Image.open(temp_file) as im:
            assert im.n_frames == 5
            assert im.is_animated

            # Check that timestamps and durations match original values specified
            ts = 0
            for frame in range(im.n_frames):
                im.seek(frame)
                im.load()
                assert im.info["duration"] == durations[frame]
                assert im.info["timestamp"] == ts
                ts += durations[frame]

    def test_seeking(self, tmp_path):
        """
        Create an animated AVIF file, and then try seeking through frames in
        reverse-order, verifying the timestamps and durations are correct.
        """

        dur = 33
        temp_file = str(tmp_path / "temp.avif")
        with self.star_frames() as frames:
            frames[0].save(
                temp_file,
                save_all=True,
                append_images=(frames[1:] + [frames[0]]),
                duration=dur,
            )

        with Image.open(temp_file) as im:
            assert im.n_frames == 5
            assert im.is_animated

            # Traverse frames in reverse, checking timestamps and durations
            ts = dur * (im.n_frames - 1)
            for frame in reversed(range(im.n_frames)):
                im.seek(frame)
                im.load()
                assert im.info["duration"] == dur
                assert im.info["timestamp"] == ts
                ts -= dur

    def test_seek_errors(self):
        with Image.open("Tests/images/avif/star.avifs") as im:
            with pytest.raises(EOFError):
                im.seek(-1)

            with pytest.raises(EOFError):
                im.seek(42)


MAX_THREADS = os.cpu_count() or 1


@skip_unless_feature("avif")
class TestAvifLeaks(PillowLeakTestCase):
    mem_limit = MAX_THREADS * 3 * 1024
    iterations = 100

    @pytest.mark.skipif(
        is_docker_qemu(), reason="Skipping on cross-architecture containers"
    )
    def test_leak_load(self):
        with open(TEST_AVIF_FILE, "rb") as f:
            im_data = f.read()

        def core():
            with Image.open(BytesIO(im_data)) as im:
                im.load()
            gc.collect()

        self._test_leak(core)
