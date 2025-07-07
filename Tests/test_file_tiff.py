from __future__ import annotations

import os
import warnings
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from types import ModuleType

import pytest

from PIL import (
    Image,
    ImageFile,
    JpegImagePlugin,
    TiffImagePlugin,
    TiffTags,
    UnidentifiedImageError,
)
from PIL.TiffImagePlugin import RESOLUTION_UNIT, X_RESOLUTION, Y_RESOLUTION

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    is_pypy,
    is_win32,
    timeout_unless_slower_valgrind,
)

ElementTree: ModuleType | None
try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None


class TestFileTiff:
    def test_sanity(self, tmp_path: Path) -> None:
        filename = tmp_path / "temp.tif"

        hopper("RGB").save(filename)

        with Image.open(filename) as im:
            im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "TIFF"

        for mode in ("1", "L", "P", "RGB", "I", "I;16", "I;16L"):
            hopper(mode).save(filename)
            with Image.open(filename):
                pass

    @pytest.mark.skipif(is_pypy(), reason="Requires CPython")
    def test_unclosed_file(self) -> None:
        def open_test_image() -> None:
            im = Image.open("Tests/images/multipage.tiff")
            im.load()

        with pytest.warns(ResourceWarning):
            open_test_image()

    def test_closed_file(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")

            im = Image.open("Tests/images/multipage.tiff")
            im.load()
            im.close()

    def test_seek_after_close(self) -> None:
        im = Image.open("Tests/images/multipage.tiff")
        assert isinstance(im, TiffImagePlugin.TiffImageFile)
        im.close()

        with pytest.raises(ValueError):
            im.n_frames
        with pytest.raises(ValueError):
            im.seek(1)

    def test_context_manager(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")

            with Image.open("Tests/images/multipage.tiff") as im:
                im.load()

    def test_mac_tiff(self) -> None:
        # Read RGBa images from macOS [@PIL136]

        filename = "Tests/images/pil136.tiff"
        with Image.open(filename) as im:
            assert im.mode == "RGBA"
            assert im.size == (55, 43)
            assert im.tile == [("raw", (0, 0, 55, 43), 8, ("RGBa", 0, 1))]
            im.load()

            assert_image_similar_tofile(im, "Tests/images/pil136.png", 1)

    def test_bigtiff(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/hopper_bigtiff.tif") as im:
            assert_image_equal_tofile(im, "Tests/images/hopper.tif")

        with Image.open("Tests/images/hopper_bigtiff.tif") as im:
            outfile = tmp_path / "temp.tif"
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            im.save(outfile, save_all=True, append_images=[im], tiffinfo=im.tag_v2)

    def test_bigtiff_save(self, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"
        im = hopper()
        im.save(outfile, big_tiff=True)

        with Image.open(outfile) as reloaded:
            assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
            assert reloaded.tag_v2._bigtiff is True

        im.save(outfile, save_all=True, append_images=[im], big_tiff=True)

        with Image.open(outfile) as reloaded:
            assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
            assert reloaded.tag_v2._bigtiff is True

    def test_seek_too_large(self) -> None:
        with pytest.raises(ValueError, match="Unable to seek to frame"):
            Image.open("Tests/images/seek_too_large.tif")

    def test_set_legacy_api(self) -> None:
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        with pytest.raises(Exception, match="Not allowing setting of legacy api"):
            ifd.legacy_api = False

    def test_xyres_tiff(self) -> None:
        filename = "Tests/images/pil168.tif"
        with Image.open(filename) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)

            # legacy api
            assert isinstance(im.tag[X_RESOLUTION][0], tuple)
            assert isinstance(im.tag[Y_RESOLUTION][0], tuple)

            # v2 api
            assert isinstance(im.tag_v2[X_RESOLUTION], TiffImagePlugin.IFDRational)
            assert isinstance(im.tag_v2[Y_RESOLUTION], TiffImagePlugin.IFDRational)

            assert im.info["dpi"] == (72.0, 72.0)

    def test_xyres_fallback_tiff(self) -> None:
        filename = "Tests/images/compression.tif"
        with Image.open(filename) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)

            # v2 api
            assert isinstance(im.tag_v2[X_RESOLUTION], TiffImagePlugin.IFDRational)
            assert isinstance(im.tag_v2[Y_RESOLUTION], TiffImagePlugin.IFDRational)
            with pytest.raises(KeyError):
                im.tag_v2[RESOLUTION_UNIT]

            # Legacy.
            assert im.info["resolution"] == (100.0, 100.0)
            # Fallback "inch".
            assert im.info["dpi"] == (100.0, 100.0)

    def test_int_resolution(self) -> None:
        filename = "Tests/images/pil168.tif"
        with Image.open(filename) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)

            # Try to read a file where X,Y_RESOLUTION are ints
            im.tag_v2[X_RESOLUTION] = 71
            im.tag_v2[Y_RESOLUTION] = 71
            im._setup()
            assert im.info["dpi"] == (71.0, 71.0)

    @pytest.mark.parametrize(
        "resolution_unit, dpi",
        [(None, 72.8), (2, 72.8), (3, 184.912)],
    )
    def test_load_float_dpi(self, resolution_unit: int | None, dpi: float) -> None:
        with Image.open(
            "Tests/images/hopper_float_dpi_" + str(resolution_unit) + ".tif"
        ) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.tag_v2.get(RESOLUTION_UNIT) == resolution_unit
            assert im.info["dpi"] == (dpi, dpi)

    def test_save_float_dpi(self, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"
        with Image.open("Tests/images/hopper.tif") as im:
            dpi = (72.2, 72.2)
            im.save(outfile, dpi=dpi)

            with Image.open(outfile) as reloaded:
                assert reloaded.info["dpi"] == dpi

    def test_save_setting_missing_resolution(self) -> None:
        b = BytesIO()
        with Image.open("Tests/images/10ct_32bit_128.tiff") as im:
            im.save(b, format="tiff", resolution=123.45)
        with Image.open(b) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.tag_v2[X_RESOLUTION] == 123.45
            assert im.tag_v2[Y_RESOLUTION] == 123.45

    def test_invalid_file(self) -> None:
        invalid_file = "Tests/images/flower.jpg"

        with pytest.raises(SyntaxError):
            TiffImagePlugin.TiffImageFile(invalid_file)

        TiffImagePlugin.PREFIXES.append(b"\xff\xd8\xff\xe0")
        with pytest.raises(SyntaxError):
            TiffImagePlugin.TiffImageFile(invalid_file)
        TiffImagePlugin.PREFIXES.pop()

    def test_bad_exif(self) -> None:
        with Image.open("Tests/images/hopper_bad_exif.jpg") as im:
            assert isinstance(im, JpegImagePlugin.JpegImageFile)

            # Should not raise struct.error.
            with pytest.warns(UserWarning, match="Corrupt EXIF data"):
                im._getexif()

    def test_save_rgba(self, tmp_path: Path) -> None:
        im = hopper("RGBA")
        outfile = tmp_path / "temp.tif"
        im.save(outfile)

    def test_save_unsupported_mode(self, tmp_path: Path) -> None:
        im = hopper("HSV")
        outfile = tmp_path / "temp.tif"
        with pytest.raises(OSError):
            im.save(outfile)

    def test_8bit_s(self) -> None:
        with Image.open("Tests/images/8bit.s.tif") as im:
            im.load()
            assert im.mode == "L"
            assert im.getpixel((50, 50)) == 184

    def test_little_endian(self) -> None:
        with Image.open("Tests/images/16bit.cropped.tif") as im:
            assert im.getpixel((0, 0)) == 480
            assert im.mode == "I;16"

            b = im.tobytes()
        # Bytes are in image native order (little endian)
        assert b[0] == ord(b"\xe0")
        assert b[1] == ord(b"\x01")

    def test_big_endian(self) -> None:
        with Image.open("Tests/images/16bit.MM.cropped.tif") as im:
            assert im.getpixel((0, 0)) == 480
            assert im.mode == "I;16B"

            b = im.tobytes()
        # Bytes are in image native order (big endian)
        assert b[0] == ord(b"\x01")
        assert b[1] == ord(b"\xe0")

    def test_16bit_r(self) -> None:
        with Image.open("Tests/images/16bit.r.tif") as im:
            assert im.getpixel((0, 0)) == 480
            assert im.mode == "I;16"

            b = im.tobytes()
        assert b[0] == ord(b"\xe0")
        assert b[1] == ord(b"\x01")

    def test_16bit_s(self) -> None:
        with Image.open("Tests/images/16bit.s.tif") as im:
            im.load()
            assert im.mode == "I"
            assert im.getpixel((0, 0)) == 32767
            assert im.getpixel((0, 1)) == 0

    def test_12bit_rawmode(self) -> None:
        """Are we generating the same interpretation
        of the image as Imagemagick is?"""

        with Image.open("Tests/images/12bit.cropped.tif") as im:
            # to make the target --
            # convert 12bit.cropped.tif -depth 16 tmp.tif
            # convert tmp.tif -evaluate RightShift 4 12in16bit2.tif
            # imagemagick will auto scale so that a 12bit FFF is 16bit FFF0,
            # so we need to unshift so that the integer values are the same.

            assert_image_equal_tofile(im, "Tests/images/12in16bit.tif")

    def test_32bit_float(self) -> None:
        # Issue 614, specific 32-bit float format
        path = "Tests/images/10ct_32bit_128.tiff"
        with Image.open(path) as im:
            im.load()

            assert im.getpixel((0, 0)) == -0.4526388943195343
            assert im.getextrema() == (-3.140936851501465, 3.140684127807617)

    def test_unknown_pixel_mode(self) -> None:
        with pytest.raises(OSError):
            with Image.open("Tests/images/hopper_unknown_pixel_mode.tif"):
                pass

    @pytest.mark.parametrize(
        "path, n_frames",
        (
            ("Tests/images/multipage-lastframe.tif", 1),
            ("Tests/images/multipage.tiff", 3),
        ),
    )
    def test_n_frames(self, path: str, n_frames: int) -> None:
        with Image.open(path) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.n_frames == n_frames
            assert im.is_animated == (n_frames != 1)

    def test_eoferror(self) -> None:
        with Image.open("Tests/images/multipage-lastframe.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            n_frames = im.n_frames

            # Test seeking past the last frame
            with pytest.raises(EOFError):
                im.seek(n_frames)
            assert im.tell() < n_frames

            # Test that seeking to the last frame does not raise an error
            im.seek(n_frames - 1)

    def test_multipage(self) -> None:
        # issue #862
        with Image.open("Tests/images/multipage.tiff") as im:
            # file is a multipage tiff: 10x10 green, 10x10 red, 20x20 blue

            im.seek(0)
            assert im.size == (10, 10)
            assert im.convert("RGB").getpixel((0, 0)) == (0, 128, 0)

            im.seek(1)
            im.load()
            assert im.size == (10, 10)
            assert im.convert("RGB").getpixel((0, 0)) == (255, 0, 0)

            im.seek(0)
            im.load()
            assert im.size == (10, 10)
            assert im.convert("RGB").getpixel((0, 0)) == (0, 128, 0)

            im.seek(2)
            im.load()
            assert im.size == (20, 20)
            assert im.convert("RGB").getpixel((0, 0)) == (0, 0, 255)

    def test_multipage_last_frame(self) -> None:
        with Image.open("Tests/images/multipage-lastframe.tif") as im:
            im.load()
            assert im.size == (20, 20)
            assert im.convert("RGB").getpixel((0, 0)) == (0, 0, 255)

    def test_frame_order(self) -> None:
        # A frame can't progress to itself after reading
        with Image.open("Tests/images/multipage_single_frame_loop.tiff") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.n_frames == 1

        # A frame can't progress to a frame that has already been read
        with Image.open("Tests/images/multipage_multiple_frame_loop.tiff") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.n_frames == 2

        # Frames don't have to be in sequence
        with Image.open("Tests/images/multipage_out_of_order.tiff") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.n_frames == 3

    def test___str__(self) -> None:
        filename = "Tests/images/pil136.tiff"
        with Image.open(filename) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)

            # Act
            ret = str(im.ifd)

            # Assert
            assert isinstance(ret, str)

    def test_dict(self) -> None:
        # Arrange
        filename = "Tests/images/pil136.tiff"
        with Image.open(filename) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)

            # v2 interface
            v2_tags = {
                256: 55,
                257: 43,
                258: (8, 8, 8, 8),
                259: 1,
                262: 2,
                296: 2,
                273: (8,),
                338: (1,),
                277: 4,
                279: (9460,),
                282: 72.0,
                283: 72.0,
                284: 1,
            }
            assert dict(im.tag_v2) == v2_tags

            # legacy interface
            legacy_tags = {
                256: (55,),
                257: (43,),
                258: (8, 8, 8, 8),
                259: (1,),
                262: (2,),
                296: (2,),
                273: (8,),
                338: (1,),
                277: (4,),
                279: (9460,),
                282: ((720000, 10000),),
                283: ((720000, 10000),),
                284: (1,),
            }
            assert dict(im.tag) == legacy_tags

    def test__delitem__(self) -> None:
        filename = "Tests/images/pil136.tiff"
        with Image.open(filename) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            len_before = len(dict(im.ifd))
            del im.ifd[256]
            len_after = len(dict(im.ifd))
            assert len_before == len_after + 1

    @pytest.mark.parametrize("legacy_api", (False, True))
    def test_load_byte(self, legacy_api: bool) -> None:
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        data = b"abc"
        ret = ifd.load_byte(data, legacy_api)
        assert ret == b"abc"

    def test_load_string(self) -> None:
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        data = b"abc\0"
        ret = ifd.load_string(data, False)
        assert ret == "abc"

    def test_load_float(self) -> None:
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        data = b"abcdabcd"
        ret = getattr(ifd, "load_float")(data, False)
        assert ret == (1.6777999408082104e22, 1.6777999408082104e22)

    def test_load_double(self) -> None:
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        data = b"abcdefghabcdefgh"
        ret = getattr(ifd, "load_double")(data, False)
        assert ret == (8.540883223036124e194, 8.540883223036124e194)

    def test_ifd_tag_type(self) -> None:
        with Image.open("Tests/images/ifd_tag_type.tiff") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert 0x8825 in im.tag_v2

    def test_exif(self, tmp_path: Path) -> None:
        def check_exif(exif: Image.Exif) -> None:
            assert sorted(exif.keys()) == [
                256,
                257,
                258,
                259,
                262,
                271,
                272,
                273,
                277,
                278,
                279,
                282,
                283,
                284,
                296,
                297,
                305,
                339,
                700,
                34665,
                34853,
                50735,
            ]
            assert exif[256] == 640
            assert exif[271] == "FLIR"

            gps = exif.get_ifd(0x8825)
            assert list(gps.keys()) == [0, 1, 2, 3, 4, 5, 6, 18]
            assert gps[0] == b"\x03\x02\x00\x00"
            assert gps[18] == "WGS-84"

        outfile = tmp_path / "temp.tif"
        with Image.open("Tests/images/ifd_tag_type.tiff") as im:
            exif = im.getexif()
            check_exif(exif)

            im.save(outfile, exif=exif)

        outfile2 = tmp_path / "temp2.tif"
        with Image.open(outfile) as im:
            exif = im.getexif()
            check_exif(exif)

            im.save(outfile2, exif=exif.tobytes())

        with Image.open(outfile2) as im:
            exif = im.getexif()
            check_exif(exif)

    def test_modify_exif(self, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"
        with Image.open("Tests/images/ifd_tag_type.tiff") as im:
            exif = im.getexif()
            exif[264] = 100

            im.save(outfile, exif=exif)

        with Image.open(outfile) as im:
            exif = im.getexif()
            assert exif[264] == 100

    def test_reload_exif_after_seek(self) -> None:
        with Image.open("Tests/images/multipage.tiff") as im:
            exif = im.getexif()
            del exif[256]
            im.seek(1)

            assert 256 in exif

    def test_exif_frames(self) -> None:
        # Test that EXIF data can change across frames
        with Image.open("Tests/images/g4-multi.tiff") as im:
            assert im.getexif()[273] == (328, 815)

            im.seek(1)
            assert im.getexif()[273] == (1408, 1907)

    @pytest.mark.parametrize("mode", ("1", "L"))
    def test_photometric(self, mode: str, tmp_path: Path) -> None:
        filename = tmp_path / "temp.tif"
        im = hopper(mode)
        im.save(filename, tiffinfo={262: 0})
        with Image.open(filename) as reloaded:
            assert isinstance(reloaded, TiffImagePlugin.TiffImageFile)
            assert reloaded.tag_v2[262] == 0
            assert_image_equal(im, reloaded)

    def test_seek(self) -> None:
        filename = "Tests/images/pil136.tiff"
        with Image.open(filename) as im:
            im.seek(0)
            assert im.tell() == 0

    def test_seek_eof(self) -> None:
        filename = "Tests/images/pil136.tiff"
        with Image.open(filename) as im:
            assert im.tell() == 0
            with pytest.raises(EOFError):
                im.seek(-1)
            with pytest.raises(EOFError):
                im.seek(1)

    def test__limit_rational_int(self) -> None:
        from PIL.TiffImagePlugin import _limit_rational

        value = 34
        ret = _limit_rational(value, 65536)
        assert ret == (34, 1)

    def test__limit_rational_float(self) -> None:
        from PIL.TiffImagePlugin import _limit_rational

        value = 22.3
        ret = _limit_rational(value, 65536)
        assert ret == (223, 10)

    def test_4bit(self) -> None:
        test_file = "Tests/images/hopper_gray_4bpp.tif"
        original = hopper("L")
        with Image.open(test_file) as im:
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

    def test_with_underscores(self, tmp_path: Path) -> None:
        kwargs = {"resolution_unit": "inch", "x_resolution": 72, "y_resolution": 36}
        filename = tmp_path / "temp.tif"
        hopper("RGB").save(filename, "TIFF", **kwargs)
        with Image.open(filename) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)

            # legacy interface
            assert im.tag[X_RESOLUTION][0][0] == 72
            assert im.tag[Y_RESOLUTION][0][0] == 36

            # v2 interface
            assert im.tag_v2[X_RESOLUTION] == 72
            assert im.tag_v2[Y_RESOLUTION] == 36

    def test_roundtrip_tiff_uint16(self, tmp_path: Path) -> None:
        # Test an image of all '0' values
        pixel_value = 0x1234
        infile = "Tests/images/uint16_1_4660.tif"
        with Image.open(infile) as im:
            assert im.getpixel((0, 0)) == pixel_value

            tmpfile = tmp_path / "temp.tif"
            im.save(tmpfile)

            assert_image_equal_tofile(im, tmpfile)

    def test_iptc(self, tmp_path: Path) -> None:
        # Do not preserve IPTC_NAA_CHUNK by default if type is LONG
        outfile = tmp_path / "temp.tif"
        with Image.open("Tests/images/hopper.tif") as im:
            im.load()
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            ifd = TiffImagePlugin.ImageFileDirectory_v2()
            ifd[33723] = 1
            ifd.tagtype[33723] = 4
            im.tag_v2 = ifd
            im.save(outfile)

        with Image.open(outfile) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert 33723 not in im.tag_v2

    def test_rowsperstrip(self, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"
        im = hopper()
        im.save(outfile, tiffinfo={278: 256})

        with Image.open(outfile) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.tag_v2[278] == 256

        im = hopper()
        im.encoderinfo = {"tiffinfo": {278: 100}}
        im2 = Image.new("L", (128, 128))
        im3 = im2.copy()
        im3.encoderinfo = {"tiffinfo": {278: 300}}
        im.save(outfile, save_all=True, tiffinfo={278: 200}, append_images=[im2, im3])

        with Image.open(outfile) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.tag_v2[278] == 100

            im.seek(1)
            assert im.tag_v2[278] == 200

            im.seek(2)
            assert im.tag_v2[278] == 300

    def test_strip_raw(self) -> None:
        infile = "Tests/images/tiff_strip_raw.tif"
        with Image.open(infile) as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_adobe_deflate.png")

    def test_strip_planar_raw(self) -> None:
        # gdal_translate -of GTiff -co INTERLEAVE=BAND \
        # tiff_strip_raw.tif tiff_strip_planar_raw.tiff
        infile = "Tests/images/tiff_strip_planar_raw.tif"
        with Image.open(infile) as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_adobe_deflate.png")

    def test_strip_planar_raw_with_overviews(self) -> None:
        # gdaladdo tiff_strip_planar_raw2.tif 2 4 8 16
        infile = "Tests/images/tiff_strip_planar_raw_with_overviews.tif"
        with Image.open(infile) as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_adobe_deflate.png")

    def test_tiled_planar_raw(self) -> None:
        # gdal_translate -of GTiff -co TILED=YES -co BLOCKXSIZE=32 \
        # -co BLOCKYSIZE=32 -co INTERLEAVE=BAND \
        # tiff_tiled_raw.tif tiff_tiled_planar_raw.tiff
        infile = "Tests/images/tiff_tiled_planar_raw.tif"
        with Image.open(infile) as im:
            assert_image_equal_tofile(im, "Tests/images/tiff_adobe_deflate.png")

    def test_planar_configuration_save(self, tmp_path: Path) -> None:
        infile = "Tests/images/tiff_tiled_planar_raw.tif"
        with Image.open(infile) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im._planar_configuration == 2

            outfile = tmp_path / "temp.tif"
            im.save(outfile)

            with Image.open(outfile) as reloaded:
                assert_image_equal_tofile(reloaded, infile)

    def test_invalid_tiled_dimensions(self) -> None:
        with open("Tests/images/tiff_tiled_planar_raw.tif", "rb") as fp:
            data = fp.read()
        b = BytesIO(data[:144] + b"\x02" + data[145:])
        with pytest.raises(ValueError):
            Image.open(b)

    @pytest.mark.parametrize("mode", ("P", "PA"))
    def test_palette(self, mode: str, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"

        im = hopper(mode)
        im.save(outfile)

        with Image.open(outfile) as reloaded:
            assert_image_equal(im.convert("RGB"), reloaded.convert("RGB"))

    def test_tiff_save_all(self) -> None:
        mp = BytesIO()
        with Image.open("Tests/images/multipage.tiff") as im:
            im.save(mp, format="tiff", save_all=True)

        mp.seek(0, os.SEEK_SET)
        with Image.open(mp) as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert im.n_frames == 3

        # Test appending images
        mp = BytesIO()
        im = Image.new("RGB", (100, 100), "#f00")
        ims = [Image.new("RGB", (100, 100), color) for color in ["#0f0", "#00f"]]
        im.copy().save(mp, format="TIFF", save_all=True, append_images=ims)

        mp.seek(0, os.SEEK_SET)
        with Image.open(mp) as reread:
            assert isinstance(reread, TiffImagePlugin.TiffImageFile)
            assert reread.n_frames == 3

        # Test appending using a generator
        def im_generator(ims: list[Image.Image]) -> Generator[Image.Image, None, None]:
            yield from ims

        mp = BytesIO()
        im.save(mp, format="TIFF", save_all=True, append_images=im_generator(ims))

        mp.seek(0, os.SEEK_SET)
        with Image.open(mp) as reread:
            assert isinstance(reread, TiffImagePlugin.TiffImageFile)
            assert reread.n_frames == 3

    def test_fixoffsets(self) -> None:
        b = BytesIO(b"II\x2a\x00\x00\x00\x00\x00")
        with TiffImagePlugin.AppendingTiffWriter(b) as a:
            b.seek(0)
            a.fixOffsets(1, isShort=True)

            b.seek(0)
            a.fixOffsets(1, isLong=True)

            # Neither short nor long
            b.seek(0)
            with pytest.raises(RuntimeError):
                a.fixOffsets(1)

        b = BytesIO(b"II\x2a\x00\x00\x00\x00\x00")
        with TiffImagePlugin.AppendingTiffWriter(b) as a:
            a.offsetOfNewPage = 2**16

            b.seek(0)
            a.fixOffsets(1, isShort=True)

        b = BytesIO(b"II\x2b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        with TiffImagePlugin.AppendingTiffWriter(b) as a:
            a.offsetOfNewPage = 2**32

            b.seek(0)
            a.fixOffsets(1, isShort=True)

            b.seek(0)
            a.fixOffsets(1, isLong=True)

    def test_appending_tiff_writer_writelong(self) -> None:
        data = b"II\x2a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b = BytesIO(data)
        with TiffImagePlugin.AppendingTiffWriter(b) as a:
            a.seek(-4, os.SEEK_CUR)
            a.writeLong(2**32 - 1)
            assert b.getvalue() == data[:-4] + b"\xff\xff\xff\xff"

    def test_appending_tiff_writer_rewritelastshorttolong(self) -> None:
        data = b"II\x2a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b = BytesIO(data)
        with TiffImagePlugin.AppendingTiffWriter(b) as a:
            a.seek(-2, os.SEEK_CUR)
            a.rewriteLastShortToLong(2**32 - 1)
            assert b.getvalue() == data[:-4] + b"\xff\xff\xff\xff"

    def test_saving_icc_profile(self, tmp_path: Path) -> None:
        # Tests saving TIFF with icc_profile set.
        # At the time of writing this will only work for non-compressed tiffs
        # as libtiff does not support embedded ICC profiles,
        # ImageFile._save(..) however does.
        im = Image.new("RGB", (1, 1))
        im.info["icc_profile"] = "Dummy value"

        # Try save-load round trip to make sure both handle icc_profile.
        tmpfile = tmp_path / "temp.tif"
        im.save(tmpfile, "TIFF", compression="raw")
        with Image.open(tmpfile) as reloaded:
            assert b"Dummy value" == reloaded.info["icc_profile"]

    def test_save_icc_profile(self, tmp_path: Path) -> None:
        im = hopper()
        assert "icc_profile" not in im.info

        outfile = tmp_path / "temp.tif"
        icc_profile = b"Dummy value"
        im.save(outfile, icc_profile=icc_profile)

        with Image.open(outfile) as reloaded:
            assert reloaded.info["icc_profile"] == icc_profile

    def test_save_bmp_compression(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/hopper.bmp") as im:
            assert im.info["compression"] == 0

            outfile = tmp_path / "temp.tif"
            im.save(outfile)

    def test_discard_icc_profile(self, tmp_path: Path) -> None:
        outfile = tmp_path / "temp.tif"

        with Image.open("Tests/images/icc_profile.png") as im:
            assert "icc_profile" in im.info

            im.save(outfile, icc_profile=None)

        with Image.open(outfile) as reloaded:
            assert "icc_profile" not in reloaded.info

    def test_getxmp(self) -> None:
        with Image.open("Tests/images/lab.tif") as im:
            if ElementTree is None:
                with pytest.warns(
                    UserWarning,
                    match="XMP data cannot be read without defusedxml dependency",
                ):
                    assert im.getxmp() == {}
            else:
                assert "xmp" in im.info
                xmp = im.getxmp()

                description = xmp["xmpmeta"]["RDF"]["Description"]
                assert description[0]["format"] == "image/tiff"
                assert description[3]["BitsPerSample"]["Seq"]["li"] == ["8", "8", "8"]

    def test_getxmp_undefined(self, tmp_path: Path) -> None:
        tmpfile = tmp_path / "temp.tif"
        im = Image.new("L", (1, 1))
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        ifd.tagtype[700] = TiffTags.UNDEFINED
        with Image.open("Tests/images/lab.tif") as im_xmp:
            ifd[700] = im_xmp.info["xmp"]
        im.save(tmpfile, tiffinfo=ifd)

        with Image.open(tmpfile) as im_reloaded:
            if ElementTree is None:
                with pytest.warns(
                    UserWarning,
                    match="XMP data cannot be read without defusedxml dependency",
                ):
                    assert im_reloaded.getxmp() == {}
            else:
                assert "xmp" in im_reloaded.info
                xmp = im_reloaded.getxmp()

                description = xmp["xmpmeta"]["RDF"]["Description"]
                assert description[0]["format"] == "image/tiff"

    def test_get_photoshop_blocks(self) -> None:
        with Image.open("Tests/images/lab.tif") as im:
            assert isinstance(im, TiffImagePlugin.TiffImageFile)
            assert list(im.get_photoshop_blocks().keys()) == [
                1061,
                1002,
                1005,
                1062,
                1037,
                1049,
                1011,
                1034,
                10000,
                1013,
                1016,
                1032,
                1054,
                1050,
                1064,
                1041,
                1044,
                1036,
                1057,
                4000,
                4001,
            ]

    def test_tiff_chunks(self, tmp_path: Path) -> None:
        tmpfile = tmp_path / "temp.tif"

        im = hopper()
        with open(tmpfile, "wb") as fp:
            for y in range(0, 128, 32):
                chunk = im.crop((0, y, 128, y + 32))
                if y == 0:
                    chunk.save(
                        fp,
                        "TIFF",
                        tiffinfo={
                            TiffImagePlugin.IMAGEWIDTH: 128,
                            TiffImagePlugin.IMAGELENGTH: 128,
                        },
                    )
                else:
                    fp.write(chunk.tobytes())

        assert_image_equal_tofile(im, tmpfile)

    def test_close_on_load_exclusive(self, tmp_path: Path) -> None:
        # similar to test_fd_leak, but runs on unixlike os
        tmpfile = tmp_path / "temp.tif"

        with Image.open("Tests/images/uint16_1_4660.tif") as im:
            im.save(tmpfile)

        im = Image.open(tmpfile)
        fp = im.fp
        assert not fp.closed
        im.load()
        assert fp.closed

    def test_close_on_load_nonexclusive(self, tmp_path: Path) -> None:
        tmpfile = tmp_path / "temp.tif"

        with Image.open("Tests/images/uint16_1_4660.tif") as im:
            im.save(tmpfile)

        with open(tmpfile, "rb") as f:
            im = Image.open(f)
            fp = im.fp
            assert not fp.closed
            im.load()
            assert not fp.closed

    # Ignore this UserWarning which triggers for four tags:
    # "Possibly corrupt EXIF data.  Expecting to read 50404352 bytes but..."
    @pytest.mark.filterwarnings("ignore:Possibly corrupt EXIF data")
    # Ignore this UserWarning:
    @pytest.mark.filterwarnings("ignore:Truncated File Read")
    @pytest.mark.skipif(
        not os.path.exists("Tests/images/string_dimension.tiff"),
        reason="Extra image files not installed",
    )
    def test_string_dimension(self) -> None:
        # Assert that an error is raised if one of the dimensions is a string
        with Image.open("Tests/images/string_dimension.tiff") as im:
            with pytest.raises(OSError):
                im.load()

    @timeout_unless_slower_valgrind(6)
    @pytest.mark.filterwarnings("ignore:Truncated File Read")
    def test_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with Image.open("Tests/images/timeout-6646305047838720") as im:
            monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
            im.load()

    @pytest.mark.parametrize(
        "test_file",
        [
            "Tests/images/oom-225817ca0f8c663be7ab4b9e717b02c661e66834.tif",
        ],
    )
    @timeout_unless_slower_valgrind(2)
    def test_oom(self, test_file: str) -> None:
        with pytest.raises(UnidentifiedImageError):
            with pytest.warns(UserWarning, match="Corrupt EXIF data"):
                with Image.open(test_file):
                    pass


@pytest.mark.skipif(not is_win32(), reason="Windows only")
class TestFileTiffW32:
    def test_fd_leak(self, tmp_path: Path) -> None:
        tmpfile = tmp_path / "temp.tif"

        # this is an mmaped file.
        with Image.open("Tests/images/uint16_1_4660.tif") as im:
            im.save(tmpfile)

        im = Image.open(tmpfile)
        fp = im.fp
        assert not fp.closed
        with pytest.raises(OSError):
            os.remove(tmpfile)
        im.load()
        assert fp.closed

        # this closes the mmap
        im.close()

        # this should not fail, as load should have closed the file pointer,
        # and close should have closed the mmap
        os.remove(tmpfile)
