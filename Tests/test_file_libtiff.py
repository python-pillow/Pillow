from __future__ import annotations

import base64
import io
import itertools
import os
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from PIL import Image, ImageFilter, ImageOps, TiffImagePlugin, TiffTags, features
from PIL.TiffImagePlugin import OSUBFILETYPE, SAMPLEFORMAT, STRIPOFFSETS, SUBIFD

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    mark_if_feature_version,
    skip_unless_feature,
)


@skip_unless_feature("libtiff")
class LibTiffTestCase:
    def _assert_noerr(self, tmp_path: Path, im: TiffImagePlugin.TiffImageFile) -> None:
        """Helper tests that assert basic sanity about the g4 tiff reading"""
        # 1 bit
        assert im.mode == "1"

        # Does the data actually load
        im.load()
        im.getdata()

        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        assert im._compression == "group4"

        # can we write it back out, in a different form.
        out = tmp_path / "temp.png"
        im.save(out)

        out_bytes = io.BytesIO()
        im.save(out_bytes, format="tiff", compression="group4")


class TestFileLibTiff(LibTiffTestCase):
    def test_version(self) -> None:
        version = features.version_codec("libtiff")
        assert version is not None
        assert re.search(r"\d+\.\d+\.\d+t?$", version)

    def test_g4_tiff(self, tmp_path: Path) -> None:
        """Test the ordinary file path load path"""

        test_file = "Tests/images/hopper_g4_500.tif"
        with Image.open(test_file) as im:
            assert im.size == (500, 500)
            self._assert_noerr(tmp_path, im)

    def test_g4_large(self, tmp_path: Path) -> None:
        test_file = "Tests/images/pport_g4.tif"
        with Image.open(test_file) as im:
            self._assert_noerr(tmp_path, im)

    def test_g4_tiff_file(self, tmp_path: Path) -> None:
        """Testing the string load path"""

        test_file = "Tests/images/hopper_g4_500.tif"
        with open(test_file, "rb") as f:
            with Image.open(f) as im:
                assert im.size == (500, 500)
                self._assert_noerr(tmp_path, im)

    def test_g4_tiff_bytesio(self, tmp_path: Path) -> None:
        """Testing the stringio loading code path"""
        test_file = "Tests/images/hopper_g4_500.tif"
        s = io.BytesIO()
        with open(test_file, "rb") as f:
            s.write(f.read())
        s.seek(0)
        with Image.open(s) as im:
            assert im.size == (500, 500)
            self._assert_noerr(tmp_path, im)

    def test_g4_non_disk_file_object(self, tmp_path: Path) -> None:
        """Testing loading from non-disk non-BytesIO file object"""
        test_file = "Tests/images/hopper_g4_500.tif"
        with open(test_file, "rb") as f:
            data = f.read()

        class NonBytesIO(io.RawIOBase):
            def read(self, size: int = -1) -> bytes:
                nonlocal data
                if size == -1:
                    size = len(data)
                result = data[:size]
                data = data[size:]
                return result

            def readable(self) -> bool:
                return True

        r = io.BufferedReader(NonBytesIO())
        with Image.open(r) as im:
            assert im.size == (500, 500)
            self._assert_noerr(tmp_path, im)

    def test_g4_eq_png(self) -> None:
        """Checking that we're actually getting the data that we expect"""
        with Image.open("Tests/images/hopper_bw_500.png") as png:
            assert_image_equal_tofile(png, "Tests/images/hopper_g4_500.tif")

    # see https://github.com/python-pillow/Pillow/issues/279
    def test_g4_fillorder_eq_png(self) -> None:
        """Checking that we're actually getting the data that we expect"""
        with Image.open("Tests/images/g4-fillorder-test.tif") as g4:
            assert_image_equal_tofile(g4, "Tests/images/g4-fillorder-test.png")

    def test_g4_write(self, tmp_path: Path) -> None:
        """Checking to see that the saved image is the same as what we wrote"""
        test_file = "Tests/images/hopper_g4_500.tif"
        with Image.open(test_file) as orig:
            out = tmp_path / "temp.tif"
            rot = orig.transpose(Image.Transpose.ROTATE_90)
            assert rot.size == (500, 500)
            rot.save(out)

            with Image.open(out) as reread:
                assert reread.size == (500, 500)
                self._assert_noerr(tmp_path, reread)
                assert_image_equal(reread, rot)
                assert reread.info["compression"] == "group4"

                assert reread.info["compression"] == orig.info["compression"]

                assert orig.tobytes() != reread.tobytes()

    def test_adobe_deflate_tiff(self) -> None:
        test_file = "Tests/images/tiff_adobe_deflate.tif"
        with Image.open(test_file) as im:
            assert im.mode == "RGB"
            assert im.size == (278, 374)
            assert im.tile[0][:3] == ("libtiff", (0, 0, 278, 374), 0)
            im.load()

            assert_image_equal_tofile(im, "Tests/images/tiff_adobe_deflate.png")

    @pytest.mark.parametrize("legacy_api", (False, True))
    def test_write_metadata(self, legacy_api: bool, tmp_path: Path) -> None:
        """Test metadata writing through libtiff"""
        f = tmp_path / "temp.tiff"
        with Image.open("Tests/images/hopper_g4.tif") as img:
            assert isinstance(img, TiffImagePlugin.TiffImageFile)
            img.save(f, tiffinfo=img.tag)

            if legacy_api:
                original = img.tag.named()
            else:
                original = img.tag_v2.named()

        # PhotometricInterpretation is set from SAVE_INFO,
        # not the original image.
        ignored = [
            "StripByteCounts",
            "RowsPerStrip",
            "PageNumber",
            "PhotometricInterpretation",
        ]

        with Image.open(f) as loaded:
            assert isinstance(loaded, TiffImagePlugin.TiffImageFile)
            if legacy_api:
                reloaded = loaded.tag.named()
            else:
                reloaded = loaded.tag_v2.named()

        for tag, value in itertools.chain(reloaded.items(), original.items()):
            if tag not in ignored:
                val = original[tag]
                if tag.endswith("Resolution"):
                    if legacy_api:
                        assert val[0][0] / val[0][1] == (
                            4294967295 / 113653537
                        ), f"{tag} didn't roundtrip"
                    else:
                        assert val == 37.79000115940079, f"{tag} didn't roundtrip"
                else:
                    assert val == value, f"{tag} didn't roundtrip"

        # https://github.com/python-pillow/Pillow/issues/1561
        requested_fields = ["StripByteCounts", "RowsPerStrip", "StripOffsets"]
        for field in requested_fields:
            assert field in reloaded, f"{field} not in metadata"

    @pytest.mark.valgrind_known_error(reason="Known invalid metadata")
    def test_additional_metadata(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # these should not crash. Seriously dummy data, most of it doesn't make
        # any sense, so we're running up against limits where we're asking
        # libtiff to do stupid things.

        # Get the list of the ones that we should be able to write

        core_items = {
            tag: info
            for tag, info in ((s, TiffTags.lookup(s)) for s in TiffTags.LIBTIFF_CORE)
            if info.type is not None
        }

        # Exclude ones that have special meaning
        # that we're already testing them
        with Image.open("Tests/images/hopper_g4.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            for tag in im.tag_v2:
                try:
                    del core_items[tag]
                except KeyError:
                    pass
            del core_items[320]  # colormap is special, tested below

            # Type codes:
            #     2: "ascii",
            #     3: "short",
            #     4: "long",
            #     5: "rational",
            #     12: "double",
            # Type: dummy value
            values = {
                2: "test",
                3: 1,
                4: 2**20,
                5: TiffImagePlugin.IFDRational(100, 1),
                12: 1.05,
            }

            new_ifd = TiffImagePlugin.ImageFileDirectory_v2()
            for tag, info in core_items.items():
                assert info.type is not None
                if info.length == 1:
                    new_ifd[tag] = values[info.type]
                elif not info.length:
                    new_ifd[tag] = tuple(values[info.type] for _ in range(3))
                else:
                    new_ifd[tag] = tuple(values[info.type] for _ in range(info.length))

            # Extra samples really doesn't make sense in this application.
            del new_ifd[338]

            out = tmp_path / "temp.tif"
            monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", True)

            im.save(out, tiffinfo=new_ifd)

    @pytest.mark.parametrize(
        "libtiff",
        (
            pytest.param(
                True,
                marks=pytest.mark.skipif(
                    not getattr(Image.core, "libtiff_support_custom_tags", False),
                    reason="Custom tags not supported by older libtiff",
                ),
            ),
            False,
        ),
    )
    def test_custom_metadata(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, libtiff: bool
    ) -> None:
        monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", libtiff)

        class Tc(NamedTuple):
            value: Any
            type: int
            supported_by_default: bool

        custom = {
            37000 + k: v
            for k, v in enumerate(
                [
                    Tc(4, TiffTags.SHORT, True),
                    Tc(123456789, TiffTags.LONG, True),
                    Tc(-4, TiffTags.SIGNED_BYTE, False),
                    Tc(-4, TiffTags.SIGNED_SHORT, False),
                    Tc(-123456789, TiffTags.SIGNED_LONG, False),
                    Tc(TiffImagePlugin.IFDRational(4, 7), TiffTags.RATIONAL, True),
                    Tc(4.25, TiffTags.FLOAT, True),
                    Tc(4.25, TiffTags.DOUBLE, True),
                    Tc("custom tag value", TiffTags.ASCII, True),
                    Tc(b"custom tag value", TiffTags.BYTE, True),
                    Tc((4, 5, 6), TiffTags.SHORT, True),
                    Tc((123456789, 9, 34, 234, 219387, 92432323), TiffTags.LONG, True),
                    Tc((-4, 9, 10), TiffTags.SIGNED_BYTE, False),
                    Tc((-4, 5, 6), TiffTags.SIGNED_SHORT, False),
                    Tc(
                        (-123456789, 9, 34, 234, 219387, -92432323),
                        TiffTags.SIGNED_LONG,
                        False,
                    ),
                    Tc((4.25, 5.25), TiffTags.FLOAT, True),
                    Tc((4.25, 5.25), TiffTags.DOUBLE, True),
                    # array of TIFF_BYTE requires bytes instead of tuple for backwards
                    # compatibility
                    Tc(bytes([4]), TiffTags.BYTE, True),
                    Tc(bytes((4, 9, 10)), TiffTags.BYTE, True),
                ]
            )
        }

        def check_tags(
            tiffinfo: TiffImagePlugin.ImageFileDirectory_v2 | dict[int, str],
        ) -> None:
            im = hopper()

            out = tmp_path / "temp.tif"
            im.save(out, tiffinfo=tiffinfo)

            with Image.open(out) as reloaded:
                assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
                for tag, value in tiffinfo.items():
                    reloaded_value = reloaded.tag_v2[tag]
                    if (
                        isinstance(reloaded_value, TiffImagePlugin.IFDRational)
                        and libtiff
                    ):
                        # libtiff does not support real RATIONALS
                        assert round(abs(float(reloaded_value) - float(value)), 7) == 0
                        continue

                    assert reloaded_value == value

        # Test with types
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        for tag, tagdata in custom.items():
            ifd[tag] = tagdata.value
            ifd.tagtype[tag] = tagdata.type
        check_tags(ifd)

        # Test without types. This only works for some types, int for example are
        # always encoded as LONG and not SIGNED_LONG.
        check_tags(
            {
                tag: tagdata.value
                for tag, tagdata in custom.items()
                if tagdata.supported_by_default
            }
        )

    def test_osubfiletype(self, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"
        with Image.open("Tests/images/g4_orientation_6.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            im.tag_v2[OSUBFILETYPE] = 1
            im.save(outfile)

    def test_subifd(self, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"
        with Image.open("Tests/images/g4_orientation_6.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            im.tag_v2[SUBIFD] = 10000

            # Should not segfault
            im.save(outfile)

    def test_xmlpacket_tag(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", True)

        out = tmp_path / "temp.tif"
        hopper().save(out, tiffinfo={700: b"xmlpacket tag"})

        with Image.open(out) as reloaded:
            assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
            if 700 in reloaded.tag_v2:
                assert reloaded.tag_v2[700] == b"xmlpacket tag"

    def test_int_dpi(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        # issue #1765
        im = hopper("RGB")
        out = tmp_path / "temp.tif"
        monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", True)
        im.save(out, dpi=(72, 72))
        with Image.open(out) as reloaded:
            assert reloaded.info["dpi"] == (72.0, 72.0)

    def test_g3_compression(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/hopper_g4_500.tif") as i:
            out = tmp_path / "temp.tif"
            i.save(out, compression="group3")

            with Image.open(out) as reread:
                assert reread.info["compression"] == "group3"
                assert_image_equal(reread, i)

    def test_little_endian(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/16bit.deflate.tif") as im:
            assert im.getpixel((0, 0)) == 480
            assert im.mode == "I;16"

            b = im.tobytes()
            # Bytes are in image native order (little endian)
            assert b[0] == ord(b"\xe0")
            assert b[1] == ord(b"\x01")

            out = tmp_path / "temp.tif"
            # out = "temp.le.tif"
            im.save(out)
        with Image.open(out) as reread:
            assert reread.info["compression"] == im.info["compression"]
            assert reread.getpixel((0, 0)) == 480
        # UNDONE - libtiff defaults to writing in native endian, so
        # on big endian, we'll get back mode = 'I;16B' here.

    def test_big_endian(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/16bit.MM.deflate.tif") as im:
            assert im.getpixel((0, 0)) == 480
            assert im.mode == "I;16B"

            b = im.tobytes()

            # Bytes are in image native order (big endian)
            assert b[0] == ord(b"\x01")
            assert b[1] == ord(b"\xe0")

            out = tmp_path / "temp.tif"
            im.save(out)
            with Image.open(out) as reread:
                assert reread.info["compression"] == im.info["compression"]
                assert reread.getpixel((0, 0)) == 480

    def test_g4_string_info(self, tmp_path: Path) -> None:
        """Tests String data in info directory"""
        test_file = "Tests/images/hopper_g4_500.tif"
        with Image.open(test_file) as orig:
            assert isinstance(orig, TiffImagePlugin.TiffImageFile)

            out = tmp_path / "temp.tif"

            orig.tag[269] = "temp.tif"
            orig.save(out)

        with Image.open(out) as reread:
            assert isinstance(reread, TiffImagePlugin.TiffImageFile)
            assert "temp.tif" == reread.tag_v2[269]
            assert "temp.tif" == reread.tag[269][0]

    def test_12bit_rawmode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Are we generating the same interpretation
        of the image as Imagemagick is?"""
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open("Tests/images/12bit.cropped.tif") as im:
            im.load()
            monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", False)
            # to make the target --
            # convert 12bit.cropped.tif -depth 16 tmp.tif
            # convert tmp.tif -evaluate RightShift 4 12in16bit2.tif
            # imagemagick will auto scale so that a 12bit FFF is 16bit FFF0,
            # so we need to unshift so that the integer values are the same.

            assert_image_equal_tofile(im, "Tests/images/12in16bit.tif")

    def test_blur(self, tmp_path: Path) -> None:
        # test case from irc, how to do blur on b/w image
        # and save to compressed tif.
        out = tmp_path / "temp.tif"
        with Image.open("Tests/images/pport_g4.tif") as im:
            im = im.convert("L")

        im = im.filter(ImageFilter.GaussianBlur(4))
        im.save(out, compression="tiff_adobe_deflate")

        assert_image_equal_tofile(im, out)

    def test_compressions(self, tmp_path: Path) -> None:
        # Test various tiff compressions and assert similar image content but reduced
        # file sizes.
        im = hopper("RGB")
        out = tmp_path / "temp.tif"
        im.save(out)
        size_raw = os.path.getsize(out)

        for compression in ("packbits", "tiff_lzw"):
            im.save(out, compression=compression)
            size_compressed = os.path.getsize(out)
            assert_image_equal_tofile(im, out)

        im.save(out, compression="jpeg")
        size_jpeg = os.path.getsize(out)
        with Image.open(out) as im2:
            assert_image_similar(im, im2, 30)

        im.save(out, compression="jpeg", quality=30)
        size_jpeg_30 = os.path.getsize(out)
        assert_image_similar_tofile(im2, out, 30)

        assert size_raw > size_compressed
        assert size_compressed > size_jpeg
        assert size_jpeg > size_jpeg_30

    def test_tiff_jpeg_compression(self, tmp_path: Path) -> None:
        im = hopper("RGB")
        out = tmp_path / "temp.tif"
        im.save(out, compression="tiff_jpeg")

        with Image.open(out) as reloaded:
            assert reloaded.info["compression"] == "jpeg"

    def test_tiff_deflate_compression(self, tmp_path: Path) -> None:
        im = hopper("RGB")
        out = tmp_path / "temp.tif"
        im.save(out, compression="tiff_deflate")

        with Image.open(out) as reloaded:
            assert reloaded.info["compression"] == "tiff_adobe_deflate"

    def test_quality(self, tmp_path: Path) -> None:
        im = hopper("RGB")
        out = tmp_path / "temp.tif"

        with pytest.raises(ValueError):
            im.save(out, compression="tiff_lzw", quality=50)
        with pytest.raises(ValueError):
            im.save(out, compression="jpeg", quality=-1)
        with pytest.raises(ValueError):
            im.save(out, compression="jpeg", quality=101)
        with pytest.raises(ValueError):
            im.save(out, compression="jpeg", quality="good")
        im.save(out, compression="jpeg", quality=0)
        im.save(out, compression="jpeg", quality=100)

    def test_cmyk_save(self, tmp_path: Path) -> None:
        im = hopper("CMYK")
        out = tmp_path / "temp.tif"

        im.save(out, compression="tiff_adobe_deflate")
        assert_image_equal_tofile(im, out)

    @pytest.mark.parametrize("im", (hopper("P"), Image.new("P", (1, 1), "#000")))
    def test_palette_save(
        self, im: Image.Image, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        out = tmp_path / "temp.tif"

        monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", True)
        im.save(out)

        with Image.open(out) as reloaded:
            # colormap/palette tag
            assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
            assert len(reloaded.tag_v2[320]) == 768

    @pytest.mark.parametrize("compression", ("tiff_ccitt", "group3", "group4"))
    def test_bw_compression_w_rgb(self, compression: str, tmp_path: Path) -> None:
        im = hopper("RGB")
        out = tmp_path / "temp.tif"

        with pytest.raises(OSError):
            im.save(out, compression=compression)

    def test_fp_leak(self) -> None:
        im: Image.Image | None = Image.open("Tests/images/hopper_g4_500.tif")
        assert im is not None
        fn = im.fp.fileno()

        os.fstat(fn)
        im.load()  # this should close it.
        with pytest.raises(OSError):
            os.fstat(fn)
        im = None  # this should force even more closed.
        with pytest.raises(OSError):
            os.fstat(fn)
        with pytest.raises(OSError):
            os.close(fn)

    def test_multipage(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # issue #862
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open("Tests/images/multipage.tiff") as im:
            # file is a multipage tiff,  10x10 green, 10x10 red, 20x20 blue

            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            im.seek(0)
            assert im.size == (10, 10)
            assert im.convert("RGB").getpixel((0, 0)) == (0, 128, 0)
            assert im.tag.next

            im.seek(1)
            assert im.size == (10, 10)
            assert im.convert("RGB").getpixel((0, 0)) == (255, 0, 0)
            assert im.tag.next

            im.seek(2)
            assert not im.tag.next
            assert im.size == (20, 20)
            assert im.convert("RGB").getpixel((0, 0)) == (0, 0, 255)

    def test_multipage_nframes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # issue #862
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open("Tests/images/multipage.tiff") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            frames = im.n_frames
            assert frames == 3
            for _ in range(frames):
                im.seek(0)
                # Should not raise ValueError: I/O operation on closed file
                im.load()

    def test_multipage_seek_backwards(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open("Tests/images/multipage.tiff") as im:
            im.seek(1)
            im.load()

            im.seek(0)
            assert im.convert("RGB").getpixel((0, 0)) == (0, 128, 0)

    def test__next(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open("Tests/images/hopper.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert not im.tag.next
            im.load()
            assert not im.tag.next

    def test_4bit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Arrange
        test_file = "Tests/images/hopper_gray_4bpp.tif"
        original = hopper("L")

        # Act
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open(test_file) as im:

            # Assert
            assert im.size == (128, 128)
            assert im.mode == "L"
            assert_image_similar(im, original, 7.3)

    def test_gray_semibyte_per_pixel(self) -> None:
        test_files = (
            (
                24.8,  # epsilon
                (  # group
                    "Tests/images/tiff_gray_2_4_bpp/hopper2.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper2I.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper2R.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper2IR.tif",
                ),
            ),
            (
                7.3,  # epsilon
                (  # group
                    "Tests/images/tiff_gray_2_4_bpp/hopper4.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper4I.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper4R.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper4IR.tif",
                ),
            ),
        )
        original = hopper("L")
        for epsilon, group in test_files:
            with Image.open(group[0]) as im:
                assert im.size == (128, 128)
                assert im.mode == "L"
                assert_image_similar(im, original, epsilon)
            for file in group[1:]:
                with Image.open(file) as im2:
                    assert im2.size == (128, 128)
                    assert im2.mode == "L"
                    assert_image_equal(im, im2)

    def test_save_bytesio(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # PR 1011
        # Test TIFF saving to io.BytesIO() object.

        monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", True)
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)

        # Generate test image
        pilim = hopper()

        def save_bytesio(compression: str | None = None) -> None:
            buffer_io = io.BytesIO()
            pilim.save(buffer_io, format="tiff", compression=compression)
            buffer_io.seek(0)

            with Image.open(buffer_io) as saved_im:
                assert_image_similar(pilim, saved_im, 0)

        save_bytesio()
        save_bytesio("raw")
        save_bytesio("packbits")
        save_bytesio("tiff_lzw")

    def test_save_ycbcr(self, tmp_path: Path) -> None:
        im = hopper("YCbCr")
        outfile = tmp_path / "temp.tif"
        im.save(outfile, compression="jpeg")

        with Image.open(outfile) as reloaded:
            assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
            assert reloaded.tag_v2[530] == (1, 1)
            assert reloaded.tag_v2[532] == (0, 255, 128, 255, 128, 255)

    def test_exif_ifd(self) -> None:
        out = io.BytesIO()
        with Image.open("Tests/images/tiff_adobe_deflate.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.tag_v2[34665] == 125456
            im.save(out, "TIFF")

            with Image.open(out) as reloaded:
                assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
                assert 34665 not in reloaded.tag_v2

            im.save(out, "TIFF", tiffinfo={34665: 125456})

        with Image.open(out) as reloaded:
            assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
            if Image.core.libtiff_support_custom_tags:
                assert reloaded.tag_v2[34665] == 125456

    def test_crashing_metadata(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # issue 1597
        with Image.open("Tests/images/rdf.tif") as im:
            out = tmp_path / "temp.tif"

            monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", True)
            # this shouldn't crash
            im.save(out, format="TIFF")

    def test_page_number_x_0(self, tmp_path: Path) -> None:
        # Issue 973
        # Test TIFF with tag 297 (Page Number) having value of 0 0.
        # The first number is the current page number.
        # The second is the total number of pages, zero means not available.
        outfile = tmp_path / "temp.tif"
        # Created by printing a page in Chrome to PDF, then:
        # /usr/bin/gs -q -sDEVICE=tiffg3 -sOutputFile=total-pages-zero.tif
        # -dNOPAUSE /tmp/test.pdf -c quit
        infile = "Tests/images/total-pages-zero.tif"
        with Image.open(infile) as im:
            # Should not divide by zero
            im.save(outfile)

    def test_fd_duplication(self, tmp_path: Path) -> None:
        # https://github.com/python-pillow/Pillow/issues/1651

        tmpfile = tmp_path / "temp.tif"
        with open(tmpfile, "wb") as f:
            with open("Tests/images/g4-multi.tiff", "rb") as src:
                f.write(src.read())

        im = Image.open(tmpfile)
        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        im.n_frames
        im.close()
        # Should not raise PermissionError.
        os.remove(tmpfile)

    def test_read_icc(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with Image.open("Tests/images/hopper.iccprofile.tif") as img:
            icc = img.info.get("icc_profile")
            assert icc is not None
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open("Tests/images/hopper.iccprofile.tif") as img:
            icc_libtiff = img.info.get("icc_profile")
            assert icc_libtiff is not None
        assert icc == icc_libtiff

    @pytest.mark.parametrize(
        "libtiff",
        (
            pytest.param(
                True,
                marks=pytest.mark.skipif(
                    not getattr(Image.core, "libtiff_support_custom_tags", False),
                    reason="Custom tags not supported by older libtiff",
                ),
            ),
            False,
        ),
    )
    def test_write_icc(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, libtiff: bool
    ) -> None:
        monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", libtiff)

        with Image.open("Tests/images/hopper.iccprofile.tif") as img:
            icc_profile = img.info["icc_profile"]

            out = tmp_path / "temp.tif"
            img.save(out, icc_profile=icc_profile)
        with Image.open(out) as reloaded:
            assert icc_profile == reloaded.info["icc_profile"]

    def test_multipage_compression(self) -> None:
        with Image.open("Tests/images/compression.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            im.seek(0)
            assert im._compression == "tiff_ccitt"
            assert im.size == (10, 10)

            im.seek(1)
            assert im._compression == "packbits"
            assert im.size == (10, 10)
            im.load()

            im.seek(0)
            assert im._compression == "tiff_ccitt"
            assert im.size == (10, 10)
            im.load()

    def test_save_tiff_with_jpegtables(self, tmp_path: Path) -> None:
        # Arrange
        outfile = tmp_path / "temp.tif"

        # Created with ImageMagick: convert hopper.jpg hopper_jpg.tif
        # Contains JPEGTables (347) tag
        infile = "Tests/images/hopper_jpg.tif"
        with Image.open(infile) as im:
            # Act / Assert
            # Should not raise UnicodeDecodeError or anything else
            im.save(outfile)

    def test_16bit_RGB_tiff(self) -> None:
        with Image.open("Tests/images/tiff_16bit_RGB.tiff") as im:
            assert im.mode == "RGB"
            assert im.size == (100, 40)
            assert im.tile, [
                (
                    "libtiff",
                    (0, 0, 100, 40),
                    0,
                    ("RGB;16N", "tiff_adobe_deflate", False, 8),
                )
            ]
            im.load()

            assert_image_equal_tofile(im, "Tests/images/tiff_16bit_RGB_target.png")

    def test_16bit_RGBa_tiff(self) -> None:
        with Image.open("Tests/images/tiff_16bit_RGBa.tiff") as im:
            assert im.mode == "RGBA"
            assert im.size == (100, 40)
            assert im.tile, [
                ("libtiff", (0, 0, 100, 40), 0, ("RGBa;16N", "tiff_lzw", False, 38236))
            ]
            im.load()

            assert_image_equal_tofile(im, "Tests/images/tiff_16bit_RGBa_target.png")

    @skip_unless_feature("jpg")
    def test_gimp_tiff(self) -> None:
        # Read TIFF JPEG images from GIMP [@PIL168]
        filename = "Tests/images/pil168.tif"
        with Image.open(filename) as im:
            assert im.mode == "RGB"
            assert im.size == (256, 256)
            assert im.tile == [
                ("libtiff", (0, 0, 256, 256), 0, ("RGB", "jpeg", False, 5122))
            ]
            im.load()

            assert_image_equal_tofile(im, "Tests/images/pil168.png")

    def test_sampleformat(self) -> None:
        # https://github.com/python-pillow/Pillow/issues/1466
        with Image.open("Tests/images/copyleft.tiff") as im:
            assert im.mode == "RGB"

            assert_image_equal_tofile(im, "Tests/images/copyleft.png", mode="RGB")

    def test_sampleformat_write(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        im = Image.new("F", (1, 1))
        out = tmp_path / "temp.tif"
        monkeypatch.setattr(TiffImagePlugin, "WRITE_LIBTIFF", True)
        im.save(out)

        with Image.open(out) as reloaded:
            assert reloaded.mode == "F"
            assert reloaded.getexif()[SAMPLEFORMAT] == 3

    def test_lzma(self, capfd: pytest.CaptureFixture[str]) -> None:
        try:
            with Image.open("Tests/images/hopper_lzma.tif") as im:
                assert im.mode == "RGB"
                assert im.size == (128, 128)
                assert im.format == "TIFF"
                im2 = hopper()
                assert_image_similar(im, im2, 5)
        except OSError:
            captured = capfd.readouterr()
            if "LZMA compression support is not configured" in captured.err:
                pytest.skip("LZMA compression support is not configured")
            sys.stdout.write(captured.out)
            sys.stderr.write(captured.err)
            raise

    def test_webp(self, capfd: pytest.CaptureFixture[str]) -> None:
        try:
            with Image.open("Tests/images/hopper_webp.tif") as im:
                assert im.mode == "RGB"
                assert im.size == (128, 128)
                assert im.format == "TIFF"
                assert_image_similar_tofile(im, "Tests/images/hopper_webp.png", 1)
        except OSError:
            captured = capfd.readouterr()
            if "WEBP compression support is not configured" in captured.err:
                pytest.skip("WEBP compression support is not configured")
            if (
                "Compression scheme 50001 strip decoding is not implemented"
                in captured.err
            ):
                pytest.skip(
                    "Compression scheme 50001 strip decoding is not implemented"
                )
            sys.stdout.write(captured.out)
            sys.stderr.write(captured.err)
            raise

    def test_lzw(self) -> None:
        with Image.open("Tests/images/hopper_lzw.tif") as im:
            assert im.mode == "RGB"
            assert im.size == (128, 128)
            assert im.format == "TIFF"
            im2 = hopper()
            assert_image_similar(im, im2, 5)

    def test_strip_cmyk_jpeg(self) -> None:
        infile = "Tests/images/tiff_strip_cmyk_jpeg.tif"
        with Image.open(infile) as im:
            assert_image_similar_tofile(im, "Tests/images/pil_sample_cmyk.jpg", 0.5)

    def test_strip_cmyk_16l_jpeg(self) -> None:
        infile = "Tests/images/tiff_strip_cmyk_16l_jpeg.tif"
        with Image.open(infile) as im:
            assert_image_similar_tofile(im, "Tests/images/pil_sample_cmyk.jpg", 0.5)

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_strip_ycbcr_jpeg_2x2_sampling(self) -> None:
        infile = "Tests/images/tiff_strip_ycbcr_jpeg_2x2_sampling.tif"
        with Image.open(infile) as im:
            assert_image_similar_tofile(im, "Tests/images/flower.jpg", 1.2)

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_strip_ycbcr_jpeg_1x1_sampling(self) -> None:
        infile = "Tests/images/tiff_strip_ycbcr_jpeg_1x1_sampling.tif"
        with Image.open(infile) as im:
            assert_image_similar_tofile(im, "Tests/images/flower2.jpg", 0.01)

    def test_tiled_cmyk_jpeg(self) -> None:
        infile = "Tests/images/tiff_tiled_cmyk_jpeg.tif"
        with Image.open(infile) as im:
            assert_image_similar_tofile(im, "Tests/images/pil_sample_cmyk.jpg", 0.5)

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_tiled_ycbcr_jpeg_1x1_sampling(self) -> None:
        infile = "Tests/images/tiff_tiled_ycbcr_jpeg_1x1_sampling.tif"
        with Image.open(infile) as im:
            assert_image_similar_tofile(im, "Tests/images/flower2.jpg", 0.01)

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_tiled_ycbcr_jpeg_2x2_sampling(self) -> None:
        infile = "Tests/images/tiff_tiled_ycbcr_jpeg_2x2_sampling.tif"
        with Image.open(infile) as im:
            assert_image_similar_tofile(im, "Tests/images/flower.jpg", 1.5)

    def test_strip_planar_rgb(self) -> None:
        # gdal_translate -co TILED=no -co INTERLEAVE=BAND -co COMPRESS=LZW \
        # tiff_strip_raw.tif tiff_strip_planar_lzw.tiff
        infile = "Tests/images/tiff_strip_planar_lzw.tiff"
        with Image.open(infile) as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_adobe_deflate.png")

    def test_tiled_planar_rgb(self) -> None:
        # gdal_translate -co TILED=yes -co INTERLEAVE=BAND -co COMPRESS=LZW \
        # tiff_tiled_raw.tif tiff_tiled_planar_lzw.tiff
        infile = "Tests/images/tiff_tiled_planar_lzw.tiff"
        with Image.open(infile) as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_adobe_deflate.png")

    def test_tiled_planar_16bit_RGB(self) -> None:
        # gdal_translate -co TILED=yes -co INTERLEAVE=BAND -co COMPRESS=LZW \
        # tiff_16bit_RGB.tiff tiff_tiled_planar_16bit_RGB.tiff
        with Image.open("Tests/images/tiff_tiled_planar_16bit_RGB.tiff") as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_16bit_RGB_target.png")

    def test_strip_planar_16bit_RGB(self) -> None:
        # gdal_translate -co TILED=no -co INTERLEAVE=BAND -co COMPRESS=LZW \
        # tiff_16bit_RGB.tiff tiff_strip_planar_16bit_RGB.tiff
        with Image.open("Tests/images/tiff_strip_planar_16bit_RGB.tiff") as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_16bit_RGB_target.png")

    def test_tiled_planar_16bit_RGBa(self) -> None:
        # gdal_translate -co TILED=yes \
        # -co INTERLEAVE=BAND -co COMPRESS=LZW -co ALPHA=PREMULTIPLIED \
        # tiff_16bit_RGBa.tiff tiff_tiled_planar_16bit_RGBa.tiff
        with Image.open("Tests/images/tiff_tiled_planar_16bit_RGBa.tiff") as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_16bit_RGBa_target.png")

    def test_strip_planar_16bit_RGBa(self) -> None:
        # gdal_translate -co TILED=no \
        # -co INTERLEAVE=BAND -co COMPRESS=LZW -co ALPHA=PREMULTIPLIED \
        # tiff_16bit_RGBa.tiff tiff_strip_planar_16bit_RGBa.tiff
        with Image.open("Tests/images/tiff_strip_planar_16bit_RGBa.tiff") as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_16bit_RGBa_target.png")

    @pytest.mark.parametrize("compression", (None, "jpeg"))
    def test_block_tile_tags(self, compression: str | None, tmp_path: Path) -> None:
        im = hopper()
        out = tmp_path / "temp.tif"

        tags = {
            TiffImagePlugin.TILEWIDTH: 256,
            TiffImagePlugin.TILELENGTH: 256,
            TiffImagePlugin.TILEOFFSETS: 256,
            TiffImagePlugin.TILEBYTECOUNTS: 256,
        }
        im.save(out, exif=tags, compression=compression)

        with Image.open(out) as reloaded:
            for tag in tags:
                assert tag not in reloaded.getexif()

    def test_old_style_jpeg(self) -> None:
        with Image.open("Tests/images/old-style-jpeg-compression.tif") as im:
            assert_image_equal_tofile(im, "Tests/images/old-style-jpeg-compression.png")

    def test_old_style_jpeg_orientation(self) -> None:
        with open("Tests/images/old-style-jpeg-compression.tif", "rb") as fp:
            data = fp.read()

        # Set EXIF Orientation to 2
        data = data[:102] + b"\x02" + data[103:]

        with Image.open(io.BytesIO(data)) as im:
            im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        assert_image_equal_tofile(im, "Tests/images/old-style-jpeg-compression.png")

    def test_open_missing_samplesperpixel(self) -> None:
        with Image.open(
            "Tests/images/old-style-jpeg-compression-no-samplesperpixel.tif"
        ) as im:
            assert_image_equal_tofile(im, "Tests/images/old-style-jpeg-compression.png")

    @pytest.mark.parametrize(
        "file_name, mode, size, tile",
        [
            (
                "tiff_wrong_bits_per_sample.tiff",
                "RGBA",
                (52, 53),
                [("raw", (0, 0, 52, 53), 160, ("RGBA", 0, 1))],
            ),
            (
                "tiff_wrong_bits_per_sample_2.tiff",
                "RGB",
                (16, 16),
                [("raw", (0, 0, 16, 16), 8, ("RGB", 0, 1))],
            ),
            (
                "tiff_wrong_bits_per_sample_3.tiff",
                "RGBA",
                (512, 256),
                [("libtiff", (0, 0, 512, 256), 0, ("RGBA", "tiff_lzw", False, 48782))],
            ),
        ],
    )
    def test_wrong_bits_per_sample(
        self,
        file_name: str,
        mode: str,
        size: tuple[int, int],
        tile: list[tuple[str, tuple[int, int, int, int], int, tuple[Any, ...]]],
    ) -> None:
        with Image.open("Tests/images/" + file_name) as im:
            assert im.mode == mode
            assert im.size == size
            assert im.tile == tile
            im.load()

    def test_no_rows_per_strip(self) -> None:
        # This image does not have a RowsPerStrip TIFF tag
        infile = "Tests/images/no_rows_per_strip.tif"
        with Image.open(infile) as im:
            im.load()
        assert im.size == (950, 975)

    def test_orientation(self) -> None:
        with Image.open("Tests/images/g4_orientation_1.tif") as base_im:
            for i in range(2, 9):
                with Image.open("Tests/images/g4_orientation_" + str(i) + ".tif") as im:
                    assert isinstance(im, TiffImagePlugin.TiffImageFile)
                    assert 274 in im.tag_v2

                    im.load()
                    assert 274 not in im.tag_v2

                    assert_image_similar(base_im, im, 0.7)

    def test_exif_transpose(self) -> None:
        with Image.open("Tests/images/g4_orientation_1.tif") as base_im:
            for i in range(2, 9):
                with Image.open("Tests/images/g4_orientation_" + str(i) + ".tif") as im:
                    im = ImageOps.exif_transpose(im)

                    assert_image_similar(base_im, im, 0.7)

    @pytest.mark.parametrize(
        "test_file",
        [
            "Tests/images/old-style-jpeg-compression-no-samplesperpixel.tif",
            "Tests/images/old-style-jpeg-compression.tif",
        ],
    )
    def test_buffering(self, test_file: str) -> None:
        # load exif first
        with open(test_file, "rb", buffering=1048576) as f:
            with Image.open(f) as im:
                exif = dict(im.getexif())

        # load image before exif
        with open(test_file, "rb", buffering=1048576) as f:
            with Image.open(f) as im2:
                im2.load()
                exif_after_load = dict(im2.getexif())

        assert exif == exif_after_load

    @pytest.mark.valgrind_known_error(reason="Backtrace in Python Core")
    def test_sampleformat_not_corrupted(self) -> None:
        # Assert that a TIFF image with SampleFormat=UINT tag is not corrupted
        # when saving to a new file.
        # Pillow 6.0 fails with "OSError: cannot identify image file".
        tiff = io.BytesIO(
            base64.b64decode(
                b"SUkqAAgAAAAPAP4ABAABAAAAAAAAAAABBAABAAAAAQAAAAEBBAABAAAAAQAA"
                b"AAIBAwADAAAAwgAAAAMBAwABAAAACAAAAAYBAwABAAAAAgAAABEBBAABAAAA"
                b"4AAAABUBAwABAAAAAwAAABYBBAABAAAAAQAAABcBBAABAAAACwAAABoBBQAB"
                b"AAAAyAAAABsBBQABAAAA0AAAABwBAwABAAAAAQAAACgBAwABAAAAAQAAAFMB"
                b"AwADAAAA2AAAAAAAAAAIAAgACAABAAAAAQAAAAEAAAABAAAAAQABAAEAAAB4"
                b"nGNgYAAAAAMAAQ=="
            )
        )
        out = io.BytesIO()
        with Image.open(tiff) as im:
            im.save(out, format="tiff")
        out.seek(0)
        with Image.open(out) as im:
            im.load()

    def test_realloc_overflow(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(TiffImagePlugin, "READ_LIBTIFF", True)
        with Image.open("Tests/images/tiff_overflow_rows_per_strip.tif") as im:
            # Assert that the error code is IMAGING_CODEC_MEMORY
            with pytest.raises(OSError, match="decoder error -9"):
                im.load()

    @pytest.mark.parametrize("compression", ("tiff_adobe_deflate", "jpeg"))
    def test_save_multistrip(self, compression: str, tmp_path: Path) -> None:
        im = hopper("RGB").resize((256, 256))
        out = tmp_path / "temp.tif"
        im.save(out, compression=compression)

        with Image.open(out) as im:
            # Assert that there are multiple strips
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert len(im.tag_v2[STRIPOFFSETS]) > 1

    @pytest.mark.parametrize("argument", (True, False))
    def test_save_single_strip(
        self, argument: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        im = hopper("RGB").resize((256, 256))
        out = tmp_path / "temp.tif"

        if not argument:
            monkeypatch.setattr(TiffImagePlugin, "STRIP_SIZE", 2**18)
        arguments: dict[str, str | int] = {"compression": "tiff_adobe_deflate"}
        if argument:
            arguments["strip_size"] = 2**18
        im.save(out, "TIFF", **arguments)

        with Image.open(out) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert len(im.tag_v2[STRIPOFFSETS]) == 1

    @pytest.mark.parametrize("compression", ("tiff_adobe_deflate", None))
    def test_save_zero(self, compression: str | None, tmp_path: Path) -> None:
        im = Image.new("RGB", (0, 0))
        out = tmp_path / "temp.tif"
        with pytest.raises(SystemError):
            im.save(out, compression=compression)

    def test_save_many_compressed(self, tmp_path: Path) -> None:
        im = hopper()
        out = tmp_path / "temp.tif"
        for _ in range(10000):
            im.save(out, compression="jpeg")

    @pytest.mark.parametrize(
        "path, sizes",
        (
            ("Tests/images/hopper.tif", ()),
            ("Tests/images/child_ifd.tiff", (16, 8)),
            ("Tests/images/child_ifd_jpeg.tiff", (20,)),
        ),
    )
    def test_get_child_images(self, path: str, sizes: tuple[int, ...]) -> None:
        with Image.open(path) as im:
            ims = im.get_child_images()

        assert len(ims) == len(sizes)
        for i, im in enumerate(ims):
            w = sizes[i]
            expected = Image.new("RGB", (w, w), "#f00")
            assert_image_similar(im, expected, 1)
