from __future__ import annotations

import gc
import os
import re
import warnings
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from PIL import (
    AvifImagePlugin,
    Image,
    ImageDraw,
    ImageFile,
    UnidentifiedImageError,
    features,
)

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


def assert_xmp_orientation(xmp: bytes, expected: int) -> None:
    assert int(xmp.split(b'tiff:Orientation="')[1].split(b'"')[0]) == expected


def roundtrip(im: ImageFile.ImageFile, **options: Any) -> ImageFile.ImageFile:
    out = BytesIO()
    im.save(out, "AVIF", **options)
    return Image.open(out)


def skip_unless_avif_decoder(codec_name: str) -> pytest.MarkDecorator:
    reason = f"{codec_name} decode not available"
    return pytest.mark.skipif(
        not HAVE_AVIF or not _avif.decoder_codec_available(codec_name), reason=reason
    )


def skip_unless_avif_encoder(codec_name: str) -> pytest.MarkDecorator:
    reason = f"{codec_name} encode not available"
    return pytest.mark.skipif(
        not HAVE_AVIF or not _avif.encoder_codec_available(codec_name), reason=reason
    )


def is_docker_qemu() -> bool:
    try:
        init_proc_exe = os.readlink("/proc/1/exe")
    except (FileNotFoundError, PermissionError):
        return False
    return "qemu" in init_proc_exe


class TestUnsupportedAvif:
    def test_unsupported(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(AvifImagePlugin, "SUPPORTED", False)

        with pytest.raises(UnidentifiedImageError):
            with pytest.warns(UserWarning, match="AVIF support not installed"):
                with Image.open(TEST_AVIF_FILE):
                    pass

    def test_unsupported_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(AvifImagePlugin, "SUPPORTED", False)

        with pytest.raises(SyntaxError):
            AvifImagePlugin.AvifImageFile(TEST_AVIF_FILE)


@skip_unless_feature("avif")
class TestFileAvif:
    def test_version(self) -> None:
        version = features.version_module("avif")
        assert version is not None
        assert re.search(r"^\d+\.\d+\.\d+$", version)

    def test_codec_version(self) -> None:
        assert AvifImagePlugin.get_codec_version("unknown") is None

        for codec_name in ("aom", "dav1d", "rav1e", "svt"):
            codec_version = AvifImagePlugin.get_codec_version(codec_name)
            if _avif.decoder_codec_available(
                codec_name
            ) or _avif.encoder_codec_available(codec_name):
                assert codec_version is not None
                assert re.search(r"^v?\d+\.\d+\.\d+(-([a-z\d])+)*$", codec_version)
            else:
                assert codec_version is None

    def test_read(self) -> None:
        """
        Can we read an AVIF file without error?
        Does it have the bits we expect?
        """

        with Image.open(TEST_AVIF_FILE) as image:
            assert image.mode == "RGB"
            assert image.size == (128, 128)
            assert image.format == "AVIF"
            assert image.get_format_mimetype() == "image/avif"
            image.getdata()

            # generated with:
            # avifdec hopper.avif hopper_avif_write.png
            assert_image_similar_tofile(
                image, "Tests/images/avif/hopper_avif_write.png", 11.5
            )

    def test_write_rgb(self, tmp_path: Path) -> None:
        """
        Can we write a RGB mode file to avif without error?
        Does it have the bits we expect?
        """

        temp_file = tmp_path / "temp.avif"

        im = hopper()
        im.save(temp_file)
        with Image.open(temp_file) as reloaded:
            assert reloaded.mode == "RGB"
            assert reloaded.size == (128, 128)
            assert reloaded.format == "AVIF"
            reloaded.getdata()

            # avifdec hopper.avif avif/hopper_avif_write.png
            assert_image_similar_tofile(
                reloaded, "Tests/images/avif/hopper_avif_write.png", 6.02
            )

            # This test asserts that the images are similar. If the average pixel
            # difference between the two images is less than the epsilon value,
            # then we're going to accept that it's a reasonable lossy version of
            # the image.
            assert_image_similar(reloaded, im, 8.62)

    def test_AvifEncoder_with_invalid_args(self) -> None:
        """
        Calling encoder functions with no arguments should result in an error.
        """
        with pytest.raises(TypeError):
            _avif.AvifEncoder()

    def test_AvifDecoder_with_invalid_args(self) -> None:
        """
        Calling decoder functions with no arguments should result in an error.
        """
        with pytest.raises(TypeError):
            _avif.AvifDecoder()

    def test_invalid_dimensions(self, tmp_path: Path) -> None:
        test_file = tmp_path / "temp.avif"
        im = Image.new("RGB", (0, 0))
        with pytest.raises(ValueError):
            im.save(test_file)

    def test_encoder_finish_none_error(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Save should raise an OSError if AvifEncoder.finish returns None"""

        class _mock_avif:
            class AvifEncoder:
                def __init__(self, *args: Any) -> None:
                    pass

                def add(self, *args: Any) -> None:
                    pass

                def finish(self) -> None:
                    return None

        monkeypatch.setattr(AvifImagePlugin, "_avif", _mock_avif)

        im = Image.new("RGB", (150, 150))
        test_file = tmp_path / "temp.avif"
        with pytest.raises(OSError):
            im.save(test_file)

    def test_no_resource_warning(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            with warnings.catch_warnings():
                warnings.simplefilter("error")

                im.save(tmp_path / "temp.avif")

    @pytest.mark.parametrize("major_brand", [b"avif", b"avis", b"mif1", b"msf1"])
    def test_accept_ftyp_brands(self, major_brand: bytes) -> None:
        data = b"\x00\x00\x00\x1cftyp%s\x00\x00\x00\x00" % major_brand
        assert AvifImagePlugin._accept(data) is True

    def test_file_pointer_could_be_reused(self) -> None:
        with open(TEST_AVIF_FILE, "rb") as blob:
            with Image.open(blob) as im:
                im.load()
            with Image.open(blob) as im:
                im.load()

    def test_background_from_gif(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/chi.gif") as im:
            original_value = im.convert("RGB").getpixel((1, 1))

            # Save as AVIF
            out_avif = tmp_path / "temp.avif"
            im.save(out_avif, save_all=True)

        # Save as GIF
        out_gif = tmp_path / "temp.gif"
        with Image.open(out_avif) as im:
            im.save(out_gif)

        with Image.open(out_gif) as reread:
            reread_value = reread.convert("RGB").getpixel((1, 1))
        difference = sum([abs(original_value[i] - reread_value[i]) for i in range(3)])
        assert difference <= 6

    def test_save_single_frame(self, tmp_path: Path) -> None:
        temp_file = tmp_path / "temp.avif"
        with Image.open("Tests/images/chi.gif") as im:
            im.save(temp_file)
        with Image.open(temp_file) as im:
            assert im.n_frames == 1

    def test_invalid_file(self) -> None:
        invalid_file = "Tests/images/flower.jpg"

        with pytest.raises(SyntaxError):
            AvifImagePlugin.AvifImageFile(invalid_file)

    def test_load_transparent_rgb(self) -> None:
        test_file = "Tests/images/avif/transparency.avif"
        with Image.open(test_file) as im:
            assert_image(im, "RGBA", (64, 64))

            # image has 876 transparent pixels
            colors = im.getchannel("A").getcolors()
            assert colors is not None
            assert colors[0] == (876, 0)

    def test_save_transparent(self, tmp_path: Path) -> None:
        im = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        assert im.getcolors() == [(100, (0, 0, 0, 0))]

        test_file = tmp_path / "temp.avif"
        im.save(test_file)

        # check if saved image contains the same transparency
        with Image.open(test_file) as im:
            assert_image(im, "RGBA", (10, 10))
            assert im.getcolors() == [(100, (0, 0, 0, 0))]

    def test_save_icc_profile(self) -> None:
        with Image.open("Tests/images/avif/icc_profile_none.avif") as im:
            assert "icc_profile" not in im.info

            with Image.open("Tests/images/avif/icc_profile.avif") as with_icc:
                expected_icc = with_icc.info["icc_profile"]
                assert expected_icc is not None

                im = roundtrip(im, icc_profile=expected_icc)
                assert im.info["icc_profile"] == expected_icc

    def test_discard_icc_profile(self) -> None:
        with Image.open("Tests/images/avif/icc_profile.avif") as im:
            im = roundtrip(im, icc_profile=None)
        assert "icc_profile" not in im.info

    def test_roundtrip_icc_profile(self) -> None:
        with Image.open("Tests/images/avif/icc_profile.avif") as im:
            expected_icc = im.info["icc_profile"]

            im = roundtrip(im)
        assert im.info["icc_profile"] == expected_icc

    def test_roundtrip_no_icc_profile(self) -> None:
        with Image.open("Tests/images/avif/icc_profile_none.avif") as im:
            assert "icc_profile" not in im.info

            im = roundtrip(im)
        assert "icc_profile" not in im.info

    def test_exif(self) -> None:
        # With an EXIF chunk
        with Image.open("Tests/images/avif/exif.avif") as im:
            exif = im.getexif()
        assert exif[274] == 1

        with Image.open("Tests/images/avif/xmp_tags_orientation.avif") as im:
            exif = im.getexif()
        assert exif[274] == 3

    @pytest.mark.parametrize("use_bytes", [True, False])
    @pytest.mark.parametrize("orientation", [1, 2, 3, 4, 5, 6, 7, 8])
    def test_exif_save(
        self,
        tmp_path: Path,
        use_bytes: bool,
        orientation: int,
    ) -> None:
        exif = Image.Exif()
        exif[274] = orientation
        exif_data = exif.tobytes()
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            im.save(test_file, exif=exif_data if use_bytes else exif)

        with Image.open(test_file) as reloaded:
            if orientation == 1:
                assert "exif" not in reloaded.info
            else:
                assert reloaded.getexif()[274] == orientation
                assert reloaded.info["exif"] == exif_data

    def test_exif_without_orientation(self, tmp_path: Path) -> None:
        exif = Image.Exif()
        exif[272] = b"test"
        exif_data = exif.tobytes()
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            im.save(test_file, exif=exif)

        with Image.open(test_file) as reloaded:
            assert reloaded.info["exif"] == exif_data

    def test_exif_invalid(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            with pytest.raises(SyntaxError):
                im.save(test_file, exif=b"invalid")

    @pytest.mark.parametrize(
        "rot, mir, exif_orientation",
        [
            (0, 0, 4),
            (0, 1, 2),
            (1, 0, 5),
            (1, 1, 7),
            (2, 0, 2),
            (2, 1, 4),
            (3, 0, 7),
            (3, 1, 5),
        ],
    )
    def test_rot_mir_exif(
        self, rot: int, mir: int, exif_orientation: int, tmp_path: Path
    ) -> None:
        with Image.open(f"Tests/images/avif/rot{rot}mir{mir}.avif") as im:
            exif = im.getexif()
            assert exif[274] == exif_orientation

            test_file = tmp_path / "temp.avif"
            im.save(test_file, exif=exif)
        with Image.open(test_file) as reloaded:
            assert reloaded.getexif()[274] == exif_orientation

    def test_xmp(self) -> None:
        with Image.open("Tests/images/avif/xmp_tags_orientation.avif") as im:
            xmp = im.info["xmp"]
        assert_xmp_orientation(xmp, 3)

    def test_xmp_save(self, tmp_path: Path) -> None:
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
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            im.save(test_file, xmp=xmp_arg)

        with Image.open(test_file) as reloaded:
            xmp = reloaded.info["xmp"]
        assert_xmp_orientation(xmp, 1)

    def test_tell(self) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            assert im.tell() == 0

    def test_seek(self) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            im.seek(0)

            with pytest.raises(EOFError):
                im.seek(1)

    @pytest.mark.parametrize("subsampling", ["4:4:4", "4:2:2", "4:2:0", "4:0:0"])
    def test_encoder_subsampling(self, tmp_path: Path, subsampling: str) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            im.save(test_file, subsampling=subsampling)

    def test_encoder_subsampling_invalid(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            with pytest.raises(ValueError):
                im.save(test_file, subsampling="foo")

    @pytest.mark.parametrize("value", ["full", "limited"])
    def test_encoder_range(self, tmp_path: Path, value: str) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            im.save(test_file, range=value)

    def test_encoder_range_invalid(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            with pytest.raises(ValueError):
                im.save(test_file, range="foo")

    @skip_unless_avif_encoder("aom")
    def test_encoder_codec_param(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            im.save(test_file, codec="aom")

    def test_encoder_codec_invalid(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            with pytest.raises(ValueError):
                im.save(test_file, codec="foo")

    @skip_unless_avif_decoder("dav1d")
    def test_decoder_codec_cannot_encode(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            with pytest.raises(ValueError):
                im.save(test_file, codec="dav1d")

    @skip_unless_avif_encoder("aom")
    @pytest.mark.parametrize(
        "advanced",
        [
            {
                "aq-mode": "1",
                "enable-chroma-deltaq": "1",
            },
            (("aq-mode", "1"), ("enable-chroma-deltaq", "1")),
            [("aq-mode", "1"), ("enable-chroma-deltaq", "1")],
        ],
    )
    def test_encoder_advanced_codec_options(
        self, advanced: dict[str, str] | Sequence[tuple[str, str]]
    ) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            ctrl_buf = BytesIO()
            im.save(ctrl_buf, "AVIF", codec="aom")
            test_buf = BytesIO()
            im.save(
                test_buf,
                "AVIF",
                codec="aom",
                advanced=advanced,
            )
            assert ctrl_buf.getvalue() != test_buf.getvalue()

    @skip_unless_avif_encoder("aom")
    @pytest.mark.parametrize("advanced", [{"foo": "bar"}, {"foo": 1234}, 1234])
    def test_encoder_advanced_codec_options_invalid(
        self, tmp_path: Path, advanced: dict[str, str] | int
    ) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            with pytest.raises(ValueError):
                im.save(test_file, codec="aom", advanced=advanced)

    @skip_unless_avif_decoder("aom")
    def test_decoder_codec_param(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(AvifImagePlugin, "DECODE_CODEC_CHOICE", "aom")

        with Image.open(TEST_AVIF_FILE) as im:
            assert im.size == (128, 128)

    @skip_unless_avif_encoder("rav1e")
    def test_encoder_codec_cannot_decode(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(AvifImagePlugin, "DECODE_CODEC_CHOICE", "rav1e")

        with pytest.raises(ValueError):
            with Image.open(TEST_AVIF_FILE):
                pass

    def test_decoder_codec_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(AvifImagePlugin, "DECODE_CODEC_CHOICE", "foo")

        with pytest.raises(ValueError):
            with Image.open(TEST_AVIF_FILE):
                pass

    @skip_unless_avif_encoder("aom")
    def test_encoder_codec_available(self) -> None:
        assert _avif.encoder_codec_available("aom") is True

    def test_encoder_codec_available_bad_params(self) -> None:
        with pytest.raises(TypeError):
            _avif.encoder_codec_available()

    @skip_unless_avif_decoder("dav1d")
    def test_encoder_codec_available_cannot_decode(self) -> None:
        assert _avif.encoder_codec_available("dav1d") is False

    def test_encoder_codec_available_invalid(self) -> None:
        assert _avif.encoder_codec_available("foo") is False

    def test_encoder_quality_valueerror(self, tmp_path: Path) -> None:
        with Image.open(TEST_AVIF_FILE) as im:
            test_file = tmp_path / "temp.avif"
            with pytest.raises(ValueError):
                im.save(test_file, quality="invalid")

    @skip_unless_avif_decoder("aom")
    def test_decoder_codec_available(self) -> None:
        assert _avif.decoder_codec_available("aom") is True

    def test_decoder_codec_available_bad_params(self) -> None:
        with pytest.raises(TypeError):
            _avif.decoder_codec_available()

    @skip_unless_avif_encoder("rav1e")
    def test_decoder_codec_available_cannot_decode(self) -> None:
        assert _avif.decoder_codec_available("rav1e") is False

    def test_decoder_codec_available_invalid(self) -> None:
        assert _avif.decoder_codec_available("foo") is False

    def test_p_mode_transparency(self, tmp_path: Path) -> None:
        im = Image.new("P", size=(64, 64))
        draw = ImageDraw.Draw(im)
        draw.rectangle(xy=[(0, 0), (32, 32)], fill=255)
        draw.rectangle(xy=[(32, 32), (64, 64)], fill=255)

        out_png = tmp_path / "temp.png"
        im.save(out_png, transparency=0)
        with Image.open(out_png) as im_png:
            out_avif = tmp_path / "temp.avif"
            im_png.save(out_avif, quality=100)

            with Image.open(out_avif) as expected:
                assert_image_similar(im_png.convert("RGBA"), expected, 0.17)

    def test_decoder_strict_flags(self) -> None:
        # This would fail if full avif strictFlags were enabled
        with Image.open("Tests/images/avif/hopper-missing-pixi.avif") as im:
            assert im.size == (128, 128)

    @skip_unless_avif_encoder("aom")
    @pytest.mark.parametrize("speed", [-1, 1, 11])
    def test_aom_optimizations(self, tmp_path: Path, speed: int) -> None:
        test_file = tmp_path / "temp.avif"
        hopper().save(test_file, codec="aom", speed=speed)

    @skip_unless_avif_encoder("svt")
    def test_svt_optimizations(self, tmp_path: Path) -> None:
        test_file = tmp_path / "temp.avif"
        hopper().save(test_file, codec="svt", speed=1)


@skip_unless_feature("avif")
class TestAvifAnimation:
    @contextmanager
    def star_frames(self) -> Generator[list[Image.Image], None, None]:
        with Image.open("Tests/images/avif/star.png") as f:
            yield [f, f.rotate(90), f.rotate(180), f.rotate(270)]

    def test_n_frames(self) -> None:
        """
        Ensure that AVIF format sets n_frames and is_animated attributes
        correctly.
        """

        with Image.open(TEST_AVIF_FILE) as im:
            assert im.n_frames == 1
            assert not im.is_animated

        with Image.open("Tests/images/avif/star.avifs") as im:
            assert im.n_frames == 5
            assert im.is_animated

    def test_write_animation_P(self, tmp_path: Path) -> None:
        """
        Convert an animated GIF to animated AVIF, then compare the frame
        count, and ensure the frames are visually similar to the originals.
        """

        with Image.open("Tests/images/avif/star.gif") as original:
            assert original.n_frames > 1

            temp_file = tmp_path / "temp.avif"
            original.save(temp_file, save_all=True)
            with Image.open(temp_file) as im:
                assert im.n_frames == original.n_frames

                # Compare first frame in P mode to frame from original GIF
                assert_image_similar(im, original.convert("RGBA"), 2)

                # Compare later frames in RGBA mode to frames from original GIF
                for frame in range(1, original.n_frames):
                    original.seek(frame)
                    im.seek(frame)
                    assert_image_similar(im, original, 2.54)

    def test_write_animation_RGBA(self, tmp_path: Path) -> None:
        """
        Write an animated AVIF from RGBA frames, and ensure the frames
        are visually similar to the originals.
        """

        def check(temp_file: Path) -> None:
            with Image.open(temp_file) as im:
                assert im.n_frames == 4

                # Compare first frame to original
                assert_image_similar(im, frame1, 2.7)

                # Compare second frame to original
                im.seek(1)
                assert_image_similar(im, frame2, 4.1)

        with self.star_frames() as frames:
            frame1 = frames[0]
            frame2 = frames[1]
            temp_file1 = tmp_path / "temp.avif"
            frames[0].copy().save(temp_file1, save_all=True, append_images=frames[1:])
            check(temp_file1)

            # Test appending using a generator
            def imGenerator(
                ims: list[Image.Image],
            ) -> Generator[Image.Image, None, None]:
                yield from ims

            temp_file2 = tmp_path / "temp_generator.avif"
            frames[0].copy().save(
                temp_file2,
                save_all=True,
                append_images=imGenerator(frames[1:]),
            )
            check(temp_file2)

    def test_sequence_dimension_mismatch_check(self, tmp_path: Path) -> None:
        temp_file = tmp_path / "temp.avif"
        frame1 = Image.new("RGB", (100, 100))
        frame2 = Image.new("RGB", (150, 150))
        with pytest.raises(ValueError):
            frame1.save(temp_file, save_all=True, append_images=[frame2])

    def test_heif_raises_unidentified_image_error(self) -> None:
        with pytest.raises(UnidentifiedImageError):
            with Image.open("Tests/images/avif/hopper.heif"):
                pass

    @pytest.mark.parametrize("alpha_premultiplied", [False, True])
    def test_alpha_premultiplied(
        self, tmp_path: Path, alpha_premultiplied: bool
    ) -> None:
        temp_file = tmp_path / "temp.avif"
        color = (200, 200, 200, 1)
        im = Image.new("RGBA", (1, 1), color)
        im.save(temp_file, alpha_premultiplied=alpha_premultiplied)

        expected = (255, 255, 255, 1) if alpha_premultiplied else color
        with Image.open(temp_file) as reloaded:
            assert reloaded.getpixel((0, 0)) == expected

    def test_timestamp_and_duration(self, tmp_path: Path) -> None:
        """
        Try passing a list of durations, and make sure the encoded
        timestamps and durations are correct.
        """

        durations = [1, 10, 20, 30, 40]
        temp_file = tmp_path / "temp.avif"
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
            timestamp = 0
            for frame in range(im.n_frames):
                im.seek(frame)
                im.load()
                assert im.info["duration"] == durations[frame]
                assert im.info["timestamp"] == timestamp
                timestamp += durations[frame]

    def test_seeking(self, tmp_path: Path) -> None:
        """
        Create an animated AVIF file, and then try seeking through frames in
        reverse-order, verifying the timestamps and durations are correct.
        """

        duration = 33
        temp_file = tmp_path / "temp.avif"
        with self.star_frames() as frames:
            frames[0].save(
                temp_file,
                save_all=True,
                append_images=(frames[1:] + [frames[0]]),
                duration=duration,
            )

        with Image.open(temp_file) as im:
            assert im.n_frames == 5
            assert im.is_animated

            # Traverse frames in reverse, checking timestamps and durations
            timestamp = duration * (im.n_frames - 1)
            for frame in reversed(range(im.n_frames)):
                im.seek(frame)
                im.load()
                assert im.info["duration"] == duration
                assert im.info["timestamp"] == timestamp
                timestamp -= duration

    def test_seek_errors(self) -> None:
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
    def test_leak_load(self) -> None:
        with open(TEST_AVIF_FILE, "rb") as f:
            im_data = f.read()

        def core() -> None:
            with Image.open(BytesIO(im_data)) as im:
                im.load()
            gc.collect()

        self._test_leak(core)
