import os
from io import BytesIO

from PIL import Image, ImageFile, JpegImagePlugin

from .helper import (
    PillowTestCase,
    cjpeg_available,
    djpeg_available,
    hopper,
    is_win32,
    unittest,
)

codecs = dir(Image.core)

TEST_FILE = "Tests/images/hopper.jpg"


class TestFileJpeg(PillowTestCase):
    def setUp(self):
        if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
            self.skipTest("jpeg support not available")

    def roundtrip(self, im, **options):
        out = BytesIO()
        im.save(out, "JPEG", **options)
        test_bytes = out.tell()
        out.seek(0)
        im = Image.open(out)
        im.bytes = test_bytes  # for testing only
        return im

    def gen_random_image(self, size, mode="RGB"):
        """ Generates a very hard to compress file
        :param size: tuple
        :param mode: optional image mode

        """
        return Image.frombytes(mode, size, os.urandom(size[0] * size[1] * len(mode)))

    def test_sanity(self):

        # internal version number
        self.assertRegex(Image.core.jpeglib_version, r"\d+\.\d+$")

        with Image.open(TEST_FILE) as im:
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "JPEG")
            self.assertEqual(im.get_format_mimetype(), "image/jpeg")

    def test_app(self):
        # Test APP/COM reader (@PIL135)
        with Image.open(TEST_FILE) as im:
            self.assertEqual(
                im.applist[0], ("APP0", b"JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00")
            )
            self.assertEqual(
                im.applist[1], ("COM", b"File written by Adobe Photoshop\xa8 4.0\x00")
            )
            self.assertEqual(len(im.applist), 2)

    def test_cmyk(self):
        # Test CMYK handling.  Thanks to Tim and Charlie for test data,
        # Michael for getting me to look one more time.
        f = "Tests/images/pil_sample_cmyk.jpg"
        with Image.open(f) as im:
            # the source image has red pixels in the upper left corner.
            c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
            self.assertEqual(c, 0.0)
            self.assertGreater(m, 0.8)
            self.assertGreater(y, 0.8)
            self.assertEqual(k, 0.0)
            # the opposite corner is black
            c, m, y, k = [
                x / 255.0 for x in im.getpixel((im.size[0] - 1, im.size[1] - 1))
            ]
            self.assertGreater(k, 0.9)
            # roundtrip, and check again
            im = self.roundtrip(im)
            c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
            self.assertEqual(c, 0.0)
            self.assertGreater(m, 0.8)
            self.assertGreater(y, 0.8)
            self.assertEqual(k, 0.0)
            c, m, y, k = [
                x / 255.0 for x in im.getpixel((im.size[0] - 1, im.size[1] - 1))
            ]
            self.assertGreater(k, 0.9)

    def test_dpi(self):
        def test(xdpi, ydpi=None):
            with Image.open(TEST_FILE) as im:
                im = self.roundtrip(im, dpi=(xdpi, ydpi or xdpi))
            return im.info.get("dpi")

        self.assertEqual(test(72), (72, 72))
        self.assertEqual(test(300), (300, 300))
        self.assertEqual(test(100, 200), (100, 200))
        self.assertIsNone(test(0))  # square pixels

    def test_icc(self):
        # Test ICC support
        with Image.open("Tests/images/rgb.jpg") as im1:
            icc_profile = im1.info["icc_profile"]
            self.assertEqual(len(icc_profile), 3144)
            # Roundtrip via physical file.
            f = self.tempfile("temp.jpg")
            im1.save(f, icc_profile=icc_profile)
        with Image.open(f) as im2:
            self.assertEqual(im2.info.get("icc_profile"), icc_profile)
            # Roundtrip via memory buffer.
            im1 = self.roundtrip(hopper())
            im2 = self.roundtrip(hopper(), icc_profile=icc_profile)
            self.assert_image_equal(im1, im2)
            self.assertFalse(im1.info.get("icc_profile"))
            self.assertTrue(im2.info.get("icc_profile"))

    def test_icc_big(self):
        # Make sure that the "extra" support handles large blocks
        def test(n):
            # The ICC APP marker can store 65519 bytes per marker, so
            # using a 4-byte test code should allow us to detect out of
            # order issues.
            icc_profile = (b"Test" * int(n / 4 + 1))[:n]
            self.assertEqual(len(icc_profile), n)  # sanity
            im1 = self.roundtrip(hopper(), icc_profile=icc_profile)
            self.assertEqual(im1.info.get("icc_profile"), icc_profile or None)

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

    def test_large_icc_meta(self):
        # https://github.com/python-pillow/Pillow/issues/148
        # Sometimes the meta data on the icc_profile block is bigger than
        # Image.MAXBLOCK or the image size.
        with Image.open("Tests/images/icc_profile_big.jpg") as im:
            f = self.tempfile("temp.jpg")
            icc_profile = im.info["icc_profile"]
            # Should not raise IOError for image with icc larger than image size.
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
        self.assert_image_equal(im1, im2)
        self.assert_image_equal(im1, im3)
        self.assertGreaterEqual(im1.bytes, im2.bytes)
        self.assertGreaterEqual(im1.bytes, im3.bytes)

    def test_optimize_large_buffer(self):
        # https://github.com/python-pillow/Pillow/issues/148
        f = self.tempfile("temp.jpg")
        # this requires ~ 1.5x Image.MAXBLOCK
        im = Image.new("RGB", (4096, 4096), 0xFF3333)
        im.save(f, format="JPEG", optimize=True)

    def test_progressive(self):
        im1 = self.roundtrip(hopper())
        im2 = self.roundtrip(hopper(), progressive=False)
        im3 = self.roundtrip(hopper(), progressive=True)
        self.assertFalse(im1.info.get("progressive"))
        self.assertFalse(im2.info.get("progressive"))
        self.assertTrue(im3.info.get("progressive"))

        self.assert_image_equal(im1, im3)
        self.assertGreaterEqual(im1.bytes, im3.bytes)

    def test_progressive_large_buffer(self):
        f = self.tempfile("temp.jpg")
        # this requires ~ 1.5x Image.MAXBLOCK
        im = Image.new("RGB", (4096, 4096), 0xFF3333)
        im.save(f, format="JPEG", progressive=True)

    def test_progressive_large_buffer_highest_quality(self):
        f = self.tempfile("temp.jpg")
        im = self.gen_random_image((255, 255))
        # this requires more bytes than pixels in the image
        im.save(f, format="JPEG", progressive=True, quality=100)

    def test_progressive_cmyk_buffer(self):
        # Issue 2272, quality 90 cmyk image is tripping the large buffer bug.
        f = BytesIO()
        im = self.gen_random_image((256, 256), "CMYK")
        im.save(f, format="JPEG", progressive=True, quality=94)

    def test_large_exif(self):
        # https://github.com/python-pillow/Pillow/issues/148
        f = self.tempfile("temp.jpg")
        im = hopper()
        im.save(f, "JPEG", quality=90, exif=b"1" * 65532)

    def test_exif_typeerror(self):
        with Image.open("Tests/images/exif_typeerror.jpg") as im:
            # Should not raise a TypeError
            im._getexif()

    def test_exif_gps(self):
        # Arrange
        with Image.open("Tests/images/exif_gps.jpg") as im:
            gps_index = 34853
            expected_exif_gps = {
                0: b"\x00\x00\x00\x01",
                2: (4294967295, 1),
                5: b"\x01",
                30: 65535,
                29: "1999:99:99 99:99:99",
            }

            # Act
            exif = im._getexif()

        # Assert
        self.assertEqual(exif[gps_index], expected_exif_gps)

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
                2: (4294967295, 1),
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
            42034: ((1, 1), (1, 1), (1, 1), (1, 1)),
            42035: "LensMake",
            34856: b"\xaa\xaa\xaa\xaa\xaa\xaa",
            282: (4294967295, 1),
            33434: (4294967295, 1),
        }

        with Image.open("Tests/images/exif_gps.jpg") as im:
            exif = im._getexif()

        for tag, value in expected_exif.items():
            self.assertEqual(value, exif[tag])

    def test_exif_gps_typeerror(self):
        with Image.open("Tests/images/exif_gps_typeerror.jpg") as im:

            # Should not raise a TypeError
            im._getexif()

    def test_progressive_compat(self):
        im1 = self.roundtrip(hopper())
        self.assertFalse(im1.info.get("progressive"))
        self.assertFalse(im1.info.get("progression"))

        im2 = self.roundtrip(hopper(), progressive=0)
        im3 = self.roundtrip(hopper(), progression=0)  # compatibility
        self.assertFalse(im2.info.get("progressive"))
        self.assertFalse(im2.info.get("progression"))
        self.assertFalse(im3.info.get("progressive"))
        self.assertFalse(im3.info.get("progression"))

        im2 = self.roundtrip(hopper(), progressive=1)
        im3 = self.roundtrip(hopper(), progression=1)  # compatibility
        self.assert_image_equal(im1, im2)
        self.assert_image_equal(im1, im3)
        self.assertTrue(im2.info.get("progressive"))
        self.assertTrue(im2.info.get("progression"))
        self.assertTrue(im3.info.get("progressive"))
        self.assertTrue(im3.info.get("progression"))

    def test_quality(self):
        im1 = self.roundtrip(hopper())
        im2 = self.roundtrip(hopper(), quality=50)
        self.assert_image(im1, im2.mode, im2.size)
        self.assertGreaterEqual(im1.bytes, im2.bytes)

    def test_smooth(self):
        im1 = self.roundtrip(hopper())
        im2 = self.roundtrip(hopper(), smooth=100)
        self.assert_image(im1, im2.mode, im2.size)

    def test_subsampling(self):
        def getsampling(im):
            layer = im.layer
            return layer[0][1:3] + layer[1][1:3] + layer[2][1:3]

        # experimental API
        im = self.roundtrip(hopper(), subsampling=-1)  # default
        self.assertEqual(getsampling(im), (2, 2, 1, 1, 1, 1))
        im = self.roundtrip(hopper(), subsampling=0)  # 4:4:4
        self.assertEqual(getsampling(im), (1, 1, 1, 1, 1, 1))
        im = self.roundtrip(hopper(), subsampling=1)  # 4:2:2
        self.assertEqual(getsampling(im), (2, 1, 1, 1, 1, 1))
        im = self.roundtrip(hopper(), subsampling=2)  # 4:2:0
        self.assertEqual(getsampling(im), (2, 2, 1, 1, 1, 1))
        im = self.roundtrip(hopper(), subsampling=3)  # default (undefined)
        self.assertEqual(getsampling(im), (2, 2, 1, 1, 1, 1))

        im = self.roundtrip(hopper(), subsampling="4:4:4")
        self.assertEqual(getsampling(im), (1, 1, 1, 1, 1, 1))
        im = self.roundtrip(hopper(), subsampling="4:2:2")
        self.assertEqual(getsampling(im), (2, 1, 1, 1, 1, 1))
        im = self.roundtrip(hopper(), subsampling="4:2:0")
        self.assertEqual(getsampling(im), (2, 2, 1, 1, 1, 1))
        im = self.roundtrip(hopper(), subsampling="4:1:1")
        self.assertEqual(getsampling(im), (2, 2, 1, 1, 1, 1))

        self.assertRaises(TypeError, self.roundtrip, hopper(), subsampling="1:1:1")

    def test_exif(self):
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            info = im._getexif()
            self.assertEqual(info[305], "Adobe Photoshop CS Macintosh")

    def test_mp(self):
        with Image.open("Tests/images/pil_sample_rgb.jpg") as im:
            self.assertIsNone(im._getmp())

    def test_quality_keep(self):
        # RGB
        with Image.open("Tests/images/hopper.jpg") as im:
            f = self.tempfile("temp.jpg")
            im.save(f, quality="keep")
        # Grayscale
        with Image.open("Tests/images/hopper_gray.jpg") as im:
            f = self.tempfile("temp.jpg")
            im.save(f, quality="keep")
        # CMYK
        with Image.open("Tests/images/pil_sample_cmyk.jpg") as im:
            f = self.tempfile("temp.jpg")
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

    def test_truncated_jpeg_should_read_all_the_data(self):
        filename = "Tests/images/truncated_jpeg.jpg"
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        with Image.open(filename) as im:
            im.load()
            ImageFile.LOAD_TRUNCATED_IMAGES = False
            self.assertIsNotNone(im.getbbox())

    def test_truncated_jpeg_throws_IOError(self):
        filename = "Tests/images/truncated_jpeg.jpg"
        with Image.open(filename) as im:
            with self.assertRaises(IOError):
                im.load()

            # Test that the error is raised if loaded a second time
            with self.assertRaises(IOError):
                im.load()

    def _n_qtables_helper(self, n, test_file):
        with Image.open(test_file) as im:
            f = self.tempfile("temp.jpg")
            im.save(f, qtables=[[n] * 64] * n)
        with Image.open(f) as im:
            self.assertEqual(len(im.quantization), n)
            reloaded = self.roundtrip(im, qtables="keep")
            self.assertEqual(im.quantization, reloaded.quantization)

    def test_qtables(self):
        with Image.open("Tests/images/hopper.jpg") as im:
            qtables = im.quantization
            reloaded = self.roundtrip(im, qtables=qtables, subsampling=0)
            self.assertEqual(im.quantization, reloaded.quantization)
            self.assert_image_similar(im, self.roundtrip(im, qtables="web_low"), 30)
            self.assert_image_similar(im, self.roundtrip(im, qtables="web_high"), 30)
            self.assert_image_similar(im, self.roundtrip(im, qtables="keep"), 30)

            # valid bounds for baseline qtable
            bounds_qtable = [int(s) for s in ("255 1 " * 32).split(None)]
            self.roundtrip(im, qtables=[bounds_qtable])

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
            self.assert_image_similar(
                im,
                self.roundtrip(
                    im, qtables=[standard_l_qtable, standard_chrominance_qtable]
                ),
                30,
            )

            # tuple of qtable lists
            self.assert_image_similar(
                im,
                self.roundtrip(
                    im, qtables=(standard_l_qtable, standard_chrominance_qtable)
                ),
                30,
            )

            # dict of qtable lists
            self.assert_image_similar(
                im,
                self.roundtrip(
                    im, qtables={0: standard_l_qtable, 1: standard_chrominance_qtable}
                ),
                30,
            )

            self._n_qtables_helper(1, "Tests/images/hopper_gray.jpg")
            self._n_qtables_helper(1, "Tests/images/pil_sample_rgb.jpg")
            self._n_qtables_helper(2, "Tests/images/pil_sample_rgb.jpg")
            self._n_qtables_helper(3, "Tests/images/pil_sample_rgb.jpg")
            self._n_qtables_helper(1, "Tests/images/pil_sample_cmyk.jpg")
            self._n_qtables_helper(2, "Tests/images/pil_sample_cmyk.jpg")
            self._n_qtables_helper(3, "Tests/images/pil_sample_cmyk.jpg")
            self._n_qtables_helper(4, "Tests/images/pil_sample_cmyk.jpg")

            # not a sequence
            self.assertRaises(ValueError, self.roundtrip, im, qtables="a")
            # sequence wrong length
            self.assertRaises(ValueError, self.roundtrip, im, qtables=[])
            # sequence wrong length
            self.assertRaises(ValueError, self.roundtrip, im, qtables=[1, 2, 3, 4, 5])

            # qtable entry not a sequence
            self.assertRaises(ValueError, self.roundtrip, im, qtables=[1])
            # qtable entry has wrong number of items
            self.assertRaises(ValueError, self.roundtrip, im, qtables=[[1, 2, 3, 4]])

    @unittest.skipUnless(djpeg_available(), "djpeg not available")
    def test_load_djpeg(self):
        with Image.open(TEST_FILE) as img:
            img.load_djpeg()
            self.assert_image_similar(img, Image.open(TEST_FILE), 0)

    @unittest.skipUnless(cjpeg_available(), "cjpeg not available")
    def test_save_cjpeg(self):
        with Image.open(TEST_FILE) as img:
            tempfile = self.tempfile("temp.jpg")
            JpegImagePlugin._save_cjpeg(img, 0, tempfile)
            # Default save quality is 75%, so a tiny bit of difference is alright
            self.assert_image_similar(img, Image.open(tempfile), 17)

    def test_no_duplicate_0x1001_tag(self):
        # Arrange
        from PIL import ExifTags

        tag_ids = {v: k for k, v in ExifTags.TAGS.items()}

        # Assert
        self.assertEqual(tag_ids["RelatedImageWidth"], 0x1001)
        self.assertEqual(tag_ids["RelatedImageLength"], 0x1002)

    def test_MAXBLOCK_scaling(self):
        im = self.gen_random_image((512, 512))
        f = self.tempfile("temp.jpeg")
        im.save(f, quality=100, optimize=True)

        with Image.open(f) as reloaded:
            # none of these should crash
            reloaded.save(f, quality="keep")
            reloaded.save(f, quality="keep", progressive=True)
            reloaded.save(f, quality="keep", optimize=True)

    def test_bad_mpo_header(self):
        """ Treat unknown MPO as JPEG """
        # Arrange

        # Act
        # Shouldn't raise error
        fn = "Tests/images/sugarshack_bad_mpo_header.jpg"
        with self.assert_warning(UserWarning, Image.open, fn) as im:

            # Assert
            self.assertEqual(im.format, "JPEG")

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
            self.assertRaises(IOError, img.save, out, "JPEG")

    def test_save_tiff_with_dpi(self):
        # Arrange
        outfile = self.tempfile("temp.tif")
        with Image.open("Tests/images/hopper.tif") as im:

            # Act
            im.save(outfile, "JPEG", dpi=im.info["dpi"])

            # Assert
            with Image.open(outfile) as reloaded:
                reloaded.load()
                self.assertEqual(im.info["dpi"], reloaded.info["dpi"])

    def test_load_dpi_rounding(self):
        # Round up
        with Image.open("Tests/images/iptc_roundUp.jpg") as im:
            self.assertEqual(im.info["dpi"], (44, 44))

        # Round down
        with Image.open("Tests/images/iptc_roundDown.jpg") as im:
            self.assertEqual(im.info["dpi"], (2, 2))

    def test_save_dpi_rounding(self):
        outfile = self.tempfile("temp.jpg")
        with Image.open("Tests/images/hopper.jpg") as im:
            im.save(outfile, dpi=(72.2, 72.2))

            with Image.open(outfile) as reloaded:
                self.assertEqual(reloaded.info["dpi"], (72, 72))

            im.save(outfile, dpi=(72.8, 72.8))

        with Image.open(outfile) as reloaded:
            self.assertEqual(reloaded.info["dpi"], (73, 73))

    def test_dpi_tuple_from_exif(self):
        # Arrange
        # This Photoshop CC 2017 image has DPI in EXIF not metadata
        # EXIF XResolution is (2000000, 10000)
        with Image.open("Tests/images/photoshop-200dpi.jpg") as im:

            # Act / Assert
            self.assertEqual(im.info.get("dpi"), (200, 200))

    def test_dpi_int_from_exif(self):
        # Arrange
        # This image has DPI in EXIF not metadata
        # EXIF XResolution is 72
        with Image.open("Tests/images/exif-72dpi-int.jpg") as im:

            # Act / Assert
            self.assertEqual(im.info.get("dpi"), (72, 72))

    def test_dpi_from_dpcm_exif(self):
        # Arrange
        # This is photoshop-200dpi.jpg with EXIF resolution unit set to cm:
        # exiftool -exif:ResolutionUnit=cm photoshop-200dpi.jpg
        with Image.open("Tests/images/exif-200dpcm.jpg") as im:

            # Act / Assert
            self.assertEqual(im.info.get("dpi"), (508, 508))

    def test_dpi_exif_zero_division(self):
        # Arrange
        # This is photoshop-200dpi.jpg with EXIF resolution set to 0/0:
        # exiftool -XResolution=0/0 -YResolution=0/0 photoshop-200dpi.jpg
        with Image.open("Tests/images/exif-dpi-zerodivision.jpg") as im:

            # Act / Assert
            # This should return the default, and not raise a ZeroDivisionError
            self.assertEqual(im.info.get("dpi"), (72, 72))

    def test_no_dpi_in_exif(self):
        # Arrange
        # This is photoshop-200dpi.jpg with resolution removed from EXIF:
        # exiftool "-*resolution*"= photoshop-200dpi.jpg
        with Image.open("Tests/images/no-dpi-in-exif.jpg") as im:

            # Act / Assert
            # "When the image resolution is unknown, 72 [dpi] is designated."
            # http://www.exiv2.org/tags.html
            self.assertEqual(im.info.get("dpi"), (72, 72))

    def test_invalid_exif(self):
        # This is no-dpi-in-exif with the tiff header of the exif block
        # hexedited from MM * to FF FF FF FF
        with Image.open("Tests/images/invalid-exif.jpg") as im:

            # This should return the default, and not a SyntaxError or
            # OSError for unidentified image.
            self.assertEqual(im.info.get("dpi"), (72, 72))

    def test_invalid_exif_x_resolution(self):
        # When no x or y resolution is defined in EXIF
        im = Image.open("Tests/images/invalid-exif-without-x-resolution.jpg")

        # This should return the default, and not a ValueError or
        # OSError for an unidentified image.
        self.assertEqual(im.info.get("dpi"), (72, 72))

    def test_ifd_offset_exif(self):
        # Arrange
        # This image has been manually hexedited to have an IFD offset of 10,
        # in contrast to normal 8
        with Image.open("Tests/images/exif-ifd-offset.jpg") as im:

            # Act / Assert
            self.assertEqual(im._getexif()[306], "2017:03:13 23:03:09")

    def test_photoshop(self):
        with Image.open("Tests/images/photoshop-200dpi.jpg") as im:
            self.assertEqual(
                im.info["photoshop"][0x03ED],
                {
                    "XResolution": 200.0,
                    "DisplayedUnitsX": 1,
                    "YResolution": 200.0,
                    "DisplayedUnitsY": 1,
                },
            )

            # Test that the image can still load, even with broken Photoshop data
            # This image had the APP13 length hexedited to be smaller
            with Image.open("Tests/images/photoshop-200dpi-broken.jpg") as im_broken:
                self.assert_image_equal(im_broken, im)

        # This image does not contain a Photoshop header string
        with Image.open("Tests/images/app13.jpg") as im:
            self.assertNotIn("photoshop", im.info)


@unittest.skipUnless(is_win32(), "Windows only")
class TestFileCloseW32(PillowTestCase):
    def setUp(self):
        if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
            self.skipTest("jpeg support not available")

    def test_fd_leak(self):
        tmpfile = self.tempfile("temp.jpg")

        with Image.open("Tests/images/hopper.jpg") as im:
            im.save(tmpfile)

        im = Image.open(tmpfile)
        fp = im.fp
        self.assertFalse(fp.closed)
        self.assertRaises(WindowsError, os.remove, tmpfile)
        im.load()
        self.assertTrue(fp.closed)
        # this should not fail, as load should have closed the file.
        os.remove(tmpfile)
