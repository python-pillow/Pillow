import os
import re
from io import BytesIO

import pytest

from PIL import (
    ExifTags,
    Image,
    ImageFile,
    ImageOps,
    JpegImagePlugin,
    UnidentifiedImageError,
    features,
)

from .helper import (
    assert_image,
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    cjpeg_available,
    djpeg_available,
    hopper,
    is_win32,
    mark_if_feature_version,
    skip_unless_feature,
)

try:
    import defusedxml.ElementTree as ElementTree
except ImportError:
    ElementTree = None

TEST_FILE = "Tests/images/hopper.jpg"


@skip_unless_feature("jpg")
class TestFileJpeg:
    def roundtrip(self, im, **options):
        out = BytesIO()
        im.save(out, "JPEG", **options)
        test_bytes = out.tell()
        out.seek(0)
        im = Image.open(out)
        im.bytes = test_bytes  # for testing only
        return im

    def gen_random_image(self, size, mode="RGB"):
        """Generates a very hard to compress file
        :param size: tuple
        :param mode: optional image mode

        """
        return Image.frombytes(mode, size, os.urandom(size[0] * size[1] * len(mode)))

    def test_sanity(self):

        # internal version number
        assert re.search(r"\d+\.\d+$", features.version_codec("jpg"))

        with Image.open(TEST_FILE) as im:
            im.load()
            assert im.mode == "RGB"
            assert im.size == (128, 128)
            assert im.format == "JPEG"
            assert im.get_format_mimetype() == "image/jpeg"

    def test_app(self):
        # Test APP/COM reader (@PIL135)
        with Image.open(TEST_FILE) as im:
            assert im.applist[0] == ("APP0", b"JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00")
            assert im.applist[1] == (
                "COM",
                b"File written by Adobe Photoshop\xa8 4.0\x00",
            )
            assert len(im.applist) == 2

            assert im.info["comment"] == b"File written by Adobe Photoshop\xa8 4.0\x00"

    def test_cmyk(self):
        # Test CMYK handling.  Thanks to Tim and Charlie for test data,
        # Michael for getting me to look one more time.
        f = "Tests/images/pil_sample_cmyk.jpg"
        with Image.open(f) as im:
            # the source image has red pixels in the upper left corner.
            c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
            assert c == 0.0
            assert m > 0.8
            assert y > 0.8
            assert k == 0.0
            # the opposite corner is black
            c, m, y, k = [
                x / 255.0 for x in im.getpixel((im.size[0] - 1, im.size[1] - 1))
            ]
            assert k > 0.9
            # roundtrip, and check again
            im = self.roundtrip(im)
            c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
            assert c == 0.0
            assert m > 0.8
            assert y > 0.8
            assert k == 0.0
            c, m, y, k = [
                x / 255.0 for x in im.getpixel((im.size[0] - 1, im.size[1] - 1))
            ]
            assert k > 0.9

    @pytest.mark.parametrize(
        "test_image_path",
        [TEST_FILE, "Tests/images/pil_sample_cmyk.jpg"],
    )
    def test_dpi(self, test_image_path):
        def test(xdpi, ydpi=None):
            with Image.open(test_image_path) as im:
                im = self.roundtrip(im, dpi=(xdpi, ydpi or xdpi))
            return im.info.get("dpi")

        assert test(72) == (72, 72)
        assert test(300) == (300, 300)
        assert test(100, 200) == (100, 200)
        assert test(0) is None  # square pixels

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_icc(self, tmp_path):
        # Test ICC support
        with Image.open("Tests/images/rgb.jpg") as im1:
            icc_profile = im1.info["icc_profile"]
            assert len(icc_profile) == 3144
            # Roundtrip via physical file.
            f = str(tmp_path / "temp.jpg")
            im1.save(f, icc_profile=icc_profile)
        with Image.open(f) as im2:
            assert im2.info.get("icc_profile") == icc_profile
            # Roundtrip via memory buffer.
            im1 = self.roundtrip(hopper())
            im2 = self.roundtrip(hopper(), icc_profile=icc_profile)
            assert_image_equal(im1, im2)
            assert not im1.info.get("icc_profile")
            assert im2.info.get("icc_profile")

    def test_icc_big(self):
        # Make sure that the "extra" support handles large blocks
        def test(n):
            # The ICC APP marker can store 65519 bytes per marker, so
            # using a 4-byte test code should allow us to detect out of
            # order issues.
            icc_profile = (b"Test" * int(n / 4 + 1))[:n]
            assert len(icc_profile) == n  # sanity
            im1 = self.roundtrip(hopper(), icc_profile=icc_profile)
            assert im1.info.get("icc_profile") == (icc_profile or None)

        test(0)
        test(1)
        test(3)
        test(4)
        test(5)
        test(65533 - 14)  # full JPEG marker block
        test(65533 - 14 + 1)  # full block plus one byte
        test(ImageFile.MAXBLOCK)  # full buffer block
        test(ImageFile.MAXBLOCK + 1)  # full buffer block plus one byte
        test(ImageFile.MAXBLOCK * 4 + 3)  # large block

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_large_icc_meta(self, tmp_path):
        # https://github.com/python-pillow/Pillow/issues/148
        # Sometimes the meta data on the icc_profile block is bigger than
        # Image.MAXBLOCK or the image size.
        with Image.open("Tests/images/icc_profile_big.jpg") as im:
            f = str(tmp_path / "temp.jpg")
            icc_profile = im.info["icc_profile"]
            # Should not raise OSError for image with icc larger than image size.
            im.save(
                f,
                format="JPEG",
                progressive=True,
                quality=95,
                icc_profile=icc_profile,
                optimize=True,
            )

    def test_optimize(self):
        im1 = self.roundtrip(hopper())
        im2 = self.roundtrip(hopper(), optimize=0)
        im3 = self.roundtrip(hopper(), optimize=1)
        assert_image_equal(im1, im2)
        assert_image_equal(im1, im3)
        assert im1.bytes >= im2.bytes
        assert im1.bytes >= im3.bytes

    def test_optimize_large_buffer(self, tmp_path):
        # https://github.com/python-pillow/Pillow/issues/148
        f = str(tmp_path / "temp.jpg")
        # this requires ~ 1.5x Image.MAXBLOCK
        im = Image.new("RGB", (4096, 4096), 0xFF3333)
        im.save(f, format="JPEG", optimize=True)

    def test_progressive(self):
        im1 = self.roundtrip(hopper())
        im2 = self.roundtrip(hopper(), progressive=False)
        im3 = self.roundtrip(hopper(), progressive=True)
        assert not im1.info.get("progressive")
        assert not im2.info.get("progressive")
        assert im3.info.get("progressive")

        assert_image_equal(im1, im3)
        assert im1.bytes >= im3.bytes

    def test_progressive_large_buffer(self, tmp_path):
        f = str(tmp_path / "temp.jpg")
        # this requires ~ 1.5x Image.MAXBLOCK
        im = Image.new("RGB", (4096, 4096), 0xFF3333)
        im.save(f, format="JPEG", progressive=True)

    def test_progressive_large_buffer_highest_quality(self, tmp_path):
        f = str(tmp_path / "temp.jpg")
        im = self.gen_random_image((255, 255))
        # this requires more bytes than pixels in the image
        im.save(f, format="JPEG", progressive=True, quality=100)

    def test_progressive_cmyk_buffer(self):
        # Issue 2272, quality 90 cmyk image is tripping the large buffer bug.
        f = BytesIO()
        im = self.gen_random_image((256, 256), "CMYK")
        im.save(f, format="JPEG", progressive=True, quality=94)

    def test_large_exif(self, tmp_path):
        # https://github.com/python-pillow/Pillow/issues/148
        f = str(tmp_path / "temp.jpg")
        im = hopper()
        im.save(f, "JPEG", quality=90, exif=b"1" * 65532)

    def test_exif_typeerror(self):
        with Image.open("Tests/images/exif_typeerror.jpg") as im:
            # Should not raise a TypeError
            im._getexif()

    def test_exif_gps(self, tmp_path):
        expected_exif_gps = {
            0: b"\x00\x00\x00\x01",
            2: 4294967295,
            5: b"\x01",
            30: 65535,
            29: "1999:99:99 99:99:99",
        }
        gps_index = 34853

        # Reading
        with Image.open("Tests/images/exif_gps.jpg") as im:
            exif = im._getexif()
            assert exif[gps_index] == expected_exif_gps

        # Writing
        f = str(tmp_path / "temp.jpg")
        exif = Image.Exif()
        exif[gps_index] = expected_exif_gps
        hopper().save(f, exif=exif)

        with Image.open(f) as reloaded:
            exif = reloaded._getexif()
            assert exif[gps_index] == expected_exif_gps

    def test_empty_exif_gps(self):
        with Image.open("Tests/images/empty_gps_ifd.jpg") as im:
            exif = im.getexif()
            del exif[0x8769]

            # Assert that it needs to be transposed
            assert exif[0x0112] == Image.TRANSVERSE

            # Assert that the GPS IFD is present and empty
            assert exif.get_ifd(0x8825) == {}

            transposed = ImageOps.exif_transpose(im)
        exif = transposed.getexif()
        assert exif.get_ifd(0x8825) == {}

        # Assert that it was transposed
        assert 0x0112 not in exif

    def test_exif_equality(self):
        # In 7.2.0, Exif rationals were changed to be read as
        # TiffImagePlugin.IFDRational. This class had a bug in __eq__,
        # breaking the self-equality of Exif data
        exifs = []
        for i in range(2):
            with Image.open("Tests/images/exif-200dpcm.jpg") as im:
                exifs.append(im._getexif())
        assert exifs[0] == exifs[1]

    def test_exif_rollback(self):
        # rolling back exif support in 3.1 to pre-3.0 formatting.
        # expected from 2.9, with b/u qualifiers switched for 3.2 compatibility
        # this test passes on 2.9 and 3.1, but not 3.0
        expected_exif = {
            34867: 4294967295,
            258: (24, 24, 24),
            36867: "2099:09:29 10:10:10",
            34853: {
                0: b"\x00\x00\x00\x01",
                2: 4294967295,
                5: b"\x01",
                30: 65535,
                29: "1999:99:99 99:99:99",
            },
            296: 65535,
            34665: 185,
            41994: 65535,
            514: 4294967295,
            271: "Make",
            272: "XXX-XXX",
            305: "PIL",
            42034: (1, 1, 1, 1),
            42035: "LensMake",
            34856: b"\xaa\xaa\xaa\xaa\xaa\xaa",
            282: 4294967295,
            33434: 4294967295,
        }

        with Image.open("Tests/images/exif_gps.jpg") as im:
            exif = im._getexif()

        for tag, value in expected_exif.items():
            assert value == exif[tag]

    def test_exif_gps_typeerror(self):
        with Image.open("Tests/images/exif_gps_typeerror.jpg") as im:

            # Should not raise a TypeError
            im._getexif()

    def test_progressive_compat(self):
        im1 = self.roundtrip(hopper())
        assert not im1.info.get("progressive")
        assert not im1.info.get("progression")

        im2 = self.roundtrip(hopper(), progressive=0)
        im3 = self.roundtrip(hopper(), progression=0)  # compatibility
        assert not im2.info.get("progressive")
        assert not im2.info.get("progression")
        assert not im3.info.get("progressive")
        assert not im3.info.get("progression")

        im2 = self.roundtrip(hopper(), progressive=1)
        im3 = self.roundtrip(hopper(), progression=1)  # compatibility
        assert_image_equal(im1, im2)
        assert_image_equal(im1, im3)
        assert im2.info.get("progressive")
        assert im2.info.get("progression")
        assert im3.info.get("progressive")
        assert im3.info.get("progression")

    def test_quality(self):
        im1 = self.roundtrip(hopper())
        im2 = self.roundtrip(hopper(), quality=50)
        assert_image(im1, im2.mode, im2.size)
        assert im1.bytes >= im2.bytes

        im3 = self.roundtrip(hopper(), quality=0)
        assert_image(im1, im3.mode, im3.size)
        assert im2.bytes > im3.bytes

    def test_smooth(self):
        im1 = self.roundtrip(hopper())
        im2 = self.roundtrip(hopper(), smooth=100)
        assert_image(im1, im2.mode, im2.size)

    def test_subsampling(self):
        def getsampling(im):
            layer = im.layer
            return layer[0][1:3] + layer[1][1:3] + layer[2][1:3]

        # experimental API
        im = self.roundtrip(hopper(), subsampling=-1)  # default
        assert getsampling(im) == (2, 2, 1, 1, 1, 1)
        im = self.roundtrip(hopper(), subsampling=0)  # 4:4:4
        assert getsampling(im) == (1, 1, 1, 1, 1, 1)
        im = self.roundtrip(hopper(), subsampling=1)  # 4:2:2
        assert getsampling(im) == (2, 1, 1, 1, 1, 1)
        im = self.roundtrip(hopper(), subsampling=2)  # 4:2:0
        assert getsampling(im) == (2, 2, 1, 1, 1, 1)
        im = self.roundtrip(hopper(), subsampling=3)  # default (undefined)
        assert getsampling(im) == (2, 2, 1, 1, 1, 1)

        im = self.roundtrip(hopper(), subsampling="4:4:4")
        assert getsampling(im) == (1, 1, 1, 1, 1, 1)
        im = self.roundtrip(hopper(), subsampling="4:2:2")
        assert getsampling(im) == (2, 1, 1, 1, 1, 1)
        im = self.roundtrip(hopper(), subsampling="4:2:0")
        assert getsampling(im) == (2, 2, 1, 1, 1, 1)
        im = self.roundtrip(hopper(), subsampling="4:1:1")
        assert getsampling(im) == (2, 2, 1, 1, 1, 1)

        with pytest.raises(TypeError):
            self.roundtrip(hopper(), subsampling="1:1:1")

    def test_exif(self):
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            info = im._getexif()
            assert info[305] == "Adobe Photoshop CS Macintosh"

    def test_mp(self):
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            assert im._getmp() is None

    def test_quality_keep(self, tmp_path):
        # RGB
        with Image.open("Tests/images/hopper.jpg") as im:
            f = str(tmp_path / "temp.jpg")
            im.save(f, quality="keep")
        # Grayscale
        with Image.open("Tests/images/hopper_gray.jpg") as im:
            f = str(tmp_path / "temp.jpg")
            im.save(f, quality="keep")
        # CMYK
        with Image.open("Tests/images/pil_sample_cmyk.jpg") as im:
            f = str(tmp_path / "temp.jpg")
            im.save(f, quality="keep")

    def test_junk_jpeg_header(self):
        # https://github.com/python-pillow/Pillow/issues/630
        filename = "Tests/images/junk_jpeg_header.jpg"
        with Image.open(filename):
            pass

    def test_ff00_jpeg_header(self):
        filename = "Tests/images/jpeg_ff00_header.jpg"
        with Image.open(filename):
            pass

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_truncated_jpeg_should_read_all_the_data(self):
        filename = "Tests/images/truncated_jpeg.jpg"
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        with Image.open(filename) as im:
            im.load()
            ImageFile.LOAD_TRUNCATED_IMAGES = False
            assert im.getbbox() is not None

    def test_truncated_jpeg_throws_oserror(self):
        filename = "Tests/images/truncated_jpeg.jpg"
        with Image.open(filename) as im:
            with pytest.raises(OSError):
                im.load()

            # Test that the error is raised if loaded a second time
            with pytest.raises(OSError):
                im.load()

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_qtables(self, tmp_path):
        def _n_qtables_helper(n, test_file):
            with Image.open(test_file) as im:
                f = str(tmp_path / "temp.jpg")
                im.save(f, qtables=[[n] * 64] * n)
            with Image.open(f) as im:
                assert len(im.quantization) == n
                reloaded = self.roundtrip(im, qtables="keep")
                assert im.quantization == reloaded.quantization
                assert max(reloaded.quantization[0]) <= 255

        with Image.open("Tests/images/hopper.jpg") as im:
            qtables = im.quantization
            reloaded = self.roundtrip(im, qtables=qtables, subsampling=0)
            assert im.quantization == reloaded.quantization
            assert_image_similar(im, self.roundtrip(im, qtables="web_low"), 30)
            assert_image_similar(im, self.roundtrip(im, qtables="web_high"), 30)
            assert_image_similar(im, self.roundtrip(im, qtables="keep"), 30)

            # valid bounds for baseline qtable
            bounds_qtable = [int(s) for s in ("255 1 " * 32).split(None)]
            im2 = self.roundtrip(im, qtables=[bounds_qtable])
            assert im2.quantization == {0: bounds_qtable}

            # values from wizard.txt in jpeg9-a src package.
            standard_l_qtable = [
                int(s)
                for s in """
                16  11  10  16  24  40  51  61
                12  12  14  19  26  58  60  55
                14  13  16  24  40  57  69  56
                14  17  22  29  51  87  80  62
                18  22  37  56  68 109 103  77
                24  35  55  64  81 104 113  92
                49  64  78  87 103 121 120 101
                72  92  95  98 112 100 103  99
                """.split(
                    None
                )
            ]

            standard_chrominance_qtable = [
                int(s)
                for s in """
                17  18  24  47  99  99  99  99
                18  21  26  66  99  99  99  99
                24  26  56  99  99  99  99  99
                47  66  99  99  99  99  99  99
                99  99  99  99  99  99  99  99
                99  99  99  99  99  99  99  99
                99  99  99  99  99  99  99  99
                99  99  99  99  99  99  99  99
                """.split(
                    None
                )
            ]
            # list of qtable lists
            assert_image_similar(
                im,
                self.roundtrip(
                    im, qtables=[standard_l_qtable, standard_chrominance_qtable]
                ),
                30,
            )

            # tuple of qtable lists
            assert_image_similar(
                im,
                self.roundtrip(
                    im, qtables=(standard_l_qtable, standard_chrominance_qtable)
                ),
                30,
            )

            # dict of qtable lists
            assert_image_similar(
                im,
                self.roundtrip(
                    im, qtables={0: standard_l_qtable, 1: standard_chrominance_qtable}
                ),
                30,
            )

            _n_qtables_helper(1, "Tests/images/hopper_gray.jpg")
            _n_qtables_helper(1, "Tests/images/pil_sample_rgb.jpg")
            _n_qtables_helper(2, "Tests/images/pil_sample_rgb.jpg")
            _n_qtables_helper(3, "Tests/images/pil_sample_rgb.jpg")
            _n_qtables_helper(1, "Tests/images/pil_sample_cmyk.jpg")
            _n_qtables_helper(2, "Tests/images/pil_sample_cmyk.jpg")
            _n_qtables_helper(3, "Tests/images/pil_sample_cmyk.jpg")
            _n_qtables_helper(4, "Tests/images/pil_sample_cmyk.jpg")

            # not a sequence
            with pytest.raises(ValueError):
                self.roundtrip(im, qtables="a")
            # sequence wrong length
            with pytest.raises(ValueError):
                self.roundtrip(im, qtables=[])
            # sequence wrong length
            with pytest.raises(ValueError):
                self.roundtrip(im, qtables=[1, 2, 3, 4, 5])

            # qtable entry not a sequence
            with pytest.raises(ValueError):
                self.roundtrip(im, qtables=[1])
            # qtable entry has wrong number of items
            with pytest.raises(ValueError):
                self.roundtrip(im, qtables=[[1, 2, 3, 4]])

    def test_load_16bit_qtables(self):
        with Image.open("Tests/images/hopper_16bit_qtables.jpg") as im:
            assert len(im.quantization) == 2
            assert len(im.quantization[0]) == 64
            assert max(im.quantization[0]) > 255

    def test_save_multiple_16bit_qtables(self):
        with Image.open("Tests/images/hopper_16bit_qtables.jpg") as im:
            im2 = self.roundtrip(im, qtables="keep")
            assert im.quantization == im2.quantization

    def test_save_single_16bit_qtable(self):
        with Image.open("Tests/images/hopper_16bit_qtables.jpg") as im:
            im2 = self.roundtrip(im, qtables={0: im.quantization[0]})
            assert len(im2.quantization) == 1
            assert im2.quantization[0] == im.quantization[0]

    def test_save_low_quality_baseline_qtables(self):
        with Image.open(TEST_FILE) as im:
            im2 = self.roundtrip(im, quality=10)
            assert len(im2.quantization) == 2
            assert max(im2.quantization[0]) <= 255
            assert max(im2.quantization[1]) <= 255

    def test_convert_dict_qtables_deprecation(self):
        with pytest.warns(DeprecationWarning):
            qtable = {0: [1, 2, 3, 4]}
            qtable2 = JpegImagePlugin.convert_dict_qtables(qtable)
            assert qtable == qtable2

    @pytest.mark.skipif(not djpeg_available(), reason="djpeg not available")
    def test_load_djpeg(self):
        with Image.open(TEST_FILE) as img:
            img.load_djpeg()
            assert_image_similar_tofile(img, TEST_FILE, 5)

    @pytest.mark.skipif(not cjpeg_available(), reason="cjpeg not available")
    def test_save_cjpeg(self, tmp_path):
        with Image.open(TEST_FILE) as img:
            tempfile = str(tmp_path / "temp.jpg")
            JpegImagePlugin._save_cjpeg(img, 0, tempfile)
            # Default save quality is 75%, so a tiny bit of difference is alright
            assert_image_similar_tofile(img, tempfile, 17)

    def test_no_duplicate_0x1001_tag(self):
        # Arrange
        tag_ids = {v: k for k, v in ExifTags.TAGS.items()}

        # Assert
        assert tag_ids["RelatedImageWidth"] == 0x1001
        assert tag_ids["RelatedImageLength"] == 0x1002

    def test_MAXBLOCK_scaling(self, tmp_path):
        im = self.gen_random_image((512, 512))
        f = str(tmp_path / "temp.jpeg")
        im.save(f, quality=100, optimize=True)

        with Image.open(f) as reloaded:
            # none of these should crash
            reloaded.save(f, quality="keep")
            reloaded.save(f, quality="keep", progressive=True)
            reloaded.save(f, quality="keep", optimize=True)

    def test_bad_mpo_header(self):
        """Treat unknown MPO as JPEG"""
        # Arrange

        # Act
        # Shouldn't raise error
        fn = "Tests/images/sugarshack_bad_mpo_header.jpg"
        with pytest.warns(UserWarning, Image.open, fn) as im:

            # Assert
            assert im.format == "JPEG"

    def test_save_correct_modes(self):
        out = BytesIO()
        for mode in ["1", "L", "RGB", "RGBX", "CMYK", "YCbCr"]:
            img = Image.new(mode, (20, 20))
            img.save(out, "JPEG")

    def test_save_wrong_modes(self):
        # ref https://github.com/python-pillow/Pillow/issues/2005
        out = BytesIO()
        for mode in ["LA", "La", "RGBA", "RGBa", "P"]:
            img = Image.new(mode, (20, 20))
            with pytest.raises(OSError):
                img.save(out, "JPEG")

    def test_save_tiff_with_dpi(self, tmp_path):
        # Arrange
        outfile = str(tmp_path / "temp.tif")
        with Image.open("Tests/images/hopper.tif") as im:

            # Act
            im.save(outfile, "JPEG", dpi=im.info["dpi"])

            # Assert
            with Image.open(outfile) as reloaded:
                reloaded.load()
                assert im.info["dpi"] == reloaded.info["dpi"]

    def test_save_dpi_rounding(self, tmp_path):
        outfile = str(tmp_path / "temp.jpg")
        with Image.open("Tests/images/hopper.jpg") as im:
            im.save(outfile, dpi=(72.2, 72.2))

            with Image.open(outfile) as reloaded:
                assert reloaded.info["dpi"] == (72, 72)

            im.save(outfile, dpi=(72.8, 72.8))

        with Image.open(outfile) as reloaded:
            assert reloaded.info["dpi"] == (73, 73)

    def test_dpi_tuple_from_exif(self):
        # Arrange
        # This Photoshop CC 2017 image has DPI in EXIF not metadata
        # EXIF XResolution is (2000000, 10000)
        with Image.open("Tests/images/photoshop-200dpi.jpg") as im:

            # Act / Assert
            assert im.info.get("dpi") == (200, 200)

    def test_dpi_int_from_exif(self):
        # Arrange
        # This image has DPI in EXIF not metadata
        # EXIF XResolution is 72
        with Image.open("Tests/images/exif-72dpi-int.jpg") as im:

            # Act / Assert
            assert im.info.get("dpi") == (72, 72)

    def test_dpi_from_dpcm_exif(self):
        # Arrange
        # This is photoshop-200dpi.jpg with EXIF resolution unit set to cm:
        # exiftool -exif:ResolutionUnit=cm photoshop-200dpi.jpg
        with Image.open("Tests/images/exif-200dpcm.jpg") as im:

            # Act / Assert
            assert im.info.get("dpi") == (508, 508)

    def test_dpi_exif_zero_division(self):
        # Arrange
        # This is photoshop-200dpi.jpg with EXIF resolution set to 0/0:
        # exiftool -XResolution=0/0 -YResolution=0/0 photoshop-200dpi.jpg
        with Image.open("Tests/images/exif-dpi-zerodivision.jpg") as im:

            # Act / Assert
            # This should return the default, and not raise a ZeroDivisionError
            assert im.info.get("dpi") == (72, 72)

    def test_dpi_exif_string(self):
        # Arrange
        # 0x011A tag in this exif contains string '300300\x02'
        with Image.open("Tests/images/broken_exif_dpi.jpg") as im:

            # Act / Assert
            # This should return the default
            assert im.info.get("dpi") == (72, 72)

    def test_no_dpi_in_exif(self):
        # Arrange
        # This is photoshop-200dpi.jpg with resolution removed from EXIF:
        # exiftool "-*resolution*"= photoshop-200dpi.jpg
        with Image.open("Tests/images/no-dpi-in-exif.jpg") as im:

            # Act / Assert
            # "When the image resolution is unknown, 72 [dpi] is designated."
            # http://www.exiv2.org/tags.html
            assert im.info.get("dpi") == (72, 72)

    def test_invalid_exif(self):
        # This is no-dpi-in-exif with the tiff header of the exif block
        # hexedited from MM * to FF FF FF FF
        with Image.open("Tests/images/invalid-exif.jpg") as im:

            # This should return the default, and not a SyntaxError or
            # OSError for unidentified image.
            assert im.info.get("dpi") == (72, 72)

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_exif_x_resolution(self, tmp_path):
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()
            assert exif[282] == 180

            out = str(tmp_path / "out.jpg")
            with pytest.warns(None) as record:
                im.save(out, exif=exif)
            assert not record

        with Image.open(out) as reloaded:
            assert reloaded.getexif()[282] == 180

    def test_invalid_exif_x_resolution(self):
        # When no x or y resolution is defined in EXIF
        with Image.open("Tests/images/invalid-exif-without-x-resolution.jpg") as im:

            # This should return the default, and not a ValueError or
            # OSError for an unidentified image.
            assert im.info.get("dpi") == (72, 72)

    def test_ifd_offset_exif(self):
        # Arrange
        # This image has been manually hexedited to have an IFD offset of 10,
        # in contrast to normal 8
        with Image.open("Tests/images/exif-ifd-offset.jpg") as im:

            # Act / Assert
            assert im._getexif()[306] == "2017:03:13 23:03:09"

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_photoshop(self):
        with Image.open("Tests/images/photoshop-200dpi.jpg") as im:
            assert im.info["photoshop"][0x03ED] == {
                "XResolution": 200.0,
                "DisplayedUnitsX": 1,
                "YResolution": 200.0,
                "DisplayedUnitsY": 1,
            }

            # Test that the image can still load, even with broken Photoshop data
            # This image had the APP13 length hexedited to be smaller
            assert_image_equal_tofile(im, "Tests/images/photoshop-200dpi-broken.jpg")

        # This image does not contain a Photoshop header string
        with Image.open("Tests/images/app13.jpg") as im:
            assert "photoshop" not in im.info

    def test_photoshop_malformed_and_multiple(self):
        with Image.open("Tests/images/app13-multiple.jpg") as im:
            assert "photoshop" in im.info
            assert 24 == len(im.info["photoshop"])
            apps_13_lengths = [len(v) for k, v in im.applist if k == "APP13"]
            assert [65504, 24] == apps_13_lengths

    def test_adobe_transform(self):
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            assert im.info["adobe_transform"] == 1

        with Image.open("Tests/images/pil_sample_cmyk.jpg") as im:
            assert im.info["adobe_transform"] == 2

        # This image has been manually hexedited
        # so that the APP14 reports its length to be 11,
        # leaving no room for "adobe_transform"
        with Image.open("Tests/images/truncated_app14.jpg") as im:
            assert "adobe" in im.info
            assert "adobe_transform" not in im.info

    def test_icc_after_SOF(self):
        with Image.open("Tests/images/icc-after-SOF.jpg") as im:
            assert im.info["icc_profile"] == b"profile"

    def test_jpeg_magic_number(self):
        size = 4097
        buffer = BytesIO(b"\xFF" * size)  # Many xFF bytes
        buffer.max_pos = 0
        orig_read = buffer.read

        def read(n=-1):
            res = orig_read(n)
            buffer.max_pos = max(buffer.max_pos, buffer.tell())
            return res

        buffer.read = read
        with pytest.raises(UnidentifiedImageError):
            with Image.open(buffer):
                pass

        # Assert the entire file has not been read
        assert 0 < buffer.max_pos < size

    def test_getxmp(self):
        with Image.open("Tests/images/xmp_test.jpg") as im:
            if ElementTree is None:
                with pytest.warns(UserWarning):
                    assert im.getxmp() == {}
            else:
                xmp = im.getxmp()

                description = xmp["xmpmeta"]["RDF"]["Description"]
                assert description["DerivedFrom"] == {
                    "documentID": "8367D410E636EA95B7DE7EBA1C43A412",
                    "originalDocumentID": "8367D410E636EA95B7DE7EBA1C43A412",
                }
                assert description["Look"]["Description"]["Group"]["Alt"]["li"] == {
                    "lang": "x-default",
                    "text": "Profiles",
                }
                assert description["ToneCurve"]["Seq"]["li"] == ["0, 0", "255, 255"]

                # Attribute
                assert description["Version"] == "10.4"

        if ElementTree is not None:
            with Image.open("Tests/images/hopper.jpg") as im:
                assert im.getxmp() == {}


@pytest.mark.skipif(not is_win32(), reason="Windows only")
@skip_unless_feature("jpg")
class TestFileCloseW32:
    def test_fd_leak(self, tmp_path):
        tmpfile = str(tmp_path / "temp.jpg")

        with Image.open("Tests/images/hopper.jpg") as im:
            im.save(tmpfile)

        im = Image.open(tmpfile)
        fp = im.fp
        assert not fp.closed
        with pytest.raises(OSError):
            os.remove(tmpfile)
        im.load()
        assert fp.closed
        # this should not fail, as load should have closed the file.
        os.remove(tmpfile)
