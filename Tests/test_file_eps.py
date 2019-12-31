import io
import unittest

from PIL import EpsImagePlugin, Image

from .helper import PillowTestCase, hopper

HAS_GHOSTSCRIPT = EpsImagePlugin.has_ghostscript()

# Our two EPS test files (they are identical except for their bounding boxes)
file1 = "Tests/images/zero_bb.eps"
file2 = "Tests/images/non_zero_bb.eps"

# Due to palletization, we'll need to convert these to RGB after load
file1_compare = "Tests/images/zero_bb.png"
file1_compare_scale2 = "Tests/images/zero_bb_scale2.png"

file2_compare = "Tests/images/non_zero_bb.png"
file2_compare_scale2 = "Tests/images/non_zero_bb_scale2.png"

# EPS test files with binary preview
file3 = "Tests/images/binary_preview_map.eps"


class TestFileEps(PillowTestCase):
    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_sanity(self):
        # Regular scale
        with Image.open(file1) as image1:
            image1.load()
            self.assertEqual(image1.mode, "RGB")
            self.assertEqual(image1.size, (460, 352))
            self.assertEqual(image1.format, "EPS")

        with Image.open(file2) as image2:
            image2.load()
            self.assertEqual(image2.mode, "RGB")
            self.assertEqual(image2.size, (360, 252))
            self.assertEqual(image2.format, "EPS")

        # Double scale
        with Image.open(file1) as image1_scale2:
            image1_scale2.load(scale=2)
            self.assertEqual(image1_scale2.mode, "RGB")
            self.assertEqual(image1_scale2.size, (920, 704))
            self.assertEqual(image1_scale2.format, "EPS")

        with Image.open(file2) as image2_scale2:
            image2_scale2.load(scale=2)
            self.assertEqual(image2_scale2.mode, "RGB")
            self.assertEqual(image2_scale2.size, (720, 504))
            self.assertEqual(image2_scale2.format, "EPS")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, EpsImagePlugin.EpsImageFile, invalid_file)

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_cmyk(self):
        with Image.open("Tests/images/pil_sample_cmyk.eps") as cmyk_image:

            self.assertEqual(cmyk_image.mode, "CMYK")
            self.assertEqual(cmyk_image.size, (100, 100))
            self.assertEqual(cmyk_image.format, "EPS")

            cmyk_image.load()
            self.assertEqual(cmyk_image.mode, "RGB")

            if "jpeg_decoder" in dir(Image.core):
                with Image.open("Tests/images/pil_sample_rgb.jpg") as target:
                    self.assert_image_similar(cmyk_image, target, 10)

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_showpage(self):
        # See https://github.com/python-pillow/Pillow/issues/2615
        with Image.open("Tests/images/reqd_showpage.eps") as plot_image:
            with Image.open("Tests/images/reqd_showpage.png") as target:
                # should not crash/hang
                plot_image.load()
                #  fonts could be slightly different
                self.assert_image_similar(plot_image, target, 6)

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_file_object(self):
        # issue 479
        with Image.open(file1) as image1:
            with open(self.tempfile("temp_file.eps"), "wb") as fh:
                image1.save(fh, "EPS")

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_iobase_object(self):
        # issue 479
        with Image.open(file1) as image1:
            with open(self.tempfile("temp_iobase.eps"), "wb") as fh:
                image1.save(fh, "EPS")

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_bytesio_object(self):
        with open(file1, "rb") as f:
            img_bytes = io.BytesIO(f.read())

        with Image.open(img_bytes) as img:
            img.load()

            with Image.open(file1_compare) as image1_scale1_compare:
                image1_scale1_compare = image1_scale1_compare.convert("RGB")
            image1_scale1_compare.load()
            self.assert_image_similar(img, image1_scale1_compare, 5)

    def test_image_mode_not_supported(self):
        im = hopper("RGBA")
        tmpfile = self.tempfile("temp.eps")
        self.assertRaises(ValueError, im.save, tmpfile)

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_render_scale1(self):
        # We need png support for these render test
        codecs = dir(Image.core)
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zip/deflate support not available")

        # Zero bounding box
        with Image.open(file1) as image1_scale1:
            image1_scale1.load()
            with Image.open(file1_compare) as image1_scale1_compare:
                image1_scale1_compare = image1_scale1_compare.convert("RGB")
            image1_scale1_compare.load()
            self.assert_image_similar(image1_scale1, image1_scale1_compare, 5)

        # Non-Zero bounding box
        with Image.open(file2) as image2_scale1:
            image2_scale1.load()
            with Image.open(file2_compare) as image2_scale1_compare:
                image2_scale1_compare = image2_scale1_compare.convert("RGB")
            image2_scale1_compare.load()
            self.assert_image_similar(image2_scale1, image2_scale1_compare, 10)

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_render_scale2(self):
        # We need png support for these render test
        codecs = dir(Image.core)
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zip/deflate support not available")

        # Zero bounding box
        with Image.open(file1) as image1_scale2:
            image1_scale2.load(scale=2)
            with Image.open(file1_compare_scale2) as image1_scale2_compare:
                image1_scale2_compare = image1_scale2_compare.convert("RGB")
            image1_scale2_compare.load()
            self.assert_image_similar(image1_scale2, image1_scale2_compare, 5)

        # Non-Zero bounding box
        with Image.open(file2) as image2_scale2:
            image2_scale2.load(scale=2)
            with Image.open(file2_compare_scale2) as image2_scale2_compare:
                image2_scale2_compare = image2_scale2_compare.convert("RGB")
            image2_scale2_compare.load()
            self.assert_image_similar(image2_scale2, image2_scale2_compare, 10)

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_resize(self):
        files = [file1, file2, "Tests/images/illu10_preview.eps"]
        for fn in files:
            with Image.open(fn) as im:
                new_size = (100, 100)
                im = im.resize(new_size)
                self.assertEqual(im.size, new_size)

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_thumbnail(self):
        # Issue #619
        # Arrange
        files = [file1, file2]
        for fn in files:
            with Image.open(file1) as im:
                new_size = (100, 100)
                im.thumbnail(new_size)
                self.assertEqual(max(im.size), max(new_size))

    def test_read_binary_preview(self):
        # Issue 302
        # open image with binary preview
        with Image.open(file3):
            pass

    def _test_readline(self, t, ending):
        ending = "Failure with line ending: %s" % (
            "".join("%s" % ord(s) for s in ending)
        )
        self.assertEqual(t.readline().strip("\r\n"), "something", ending)
        self.assertEqual(t.readline().strip("\r\n"), "else", ending)
        self.assertEqual(t.readline().strip("\r\n"), "baz", ending)
        self.assertEqual(t.readline().strip("\r\n"), "bif", ending)

    def _test_readline_io_psfile(self, test_string, ending):
        f = io.BytesIO(test_string.encode("latin-1"))
        t = EpsImagePlugin.PSFile(f)
        self._test_readline(t, ending)

    def _test_readline_file_psfile(self, test_string, ending):
        f = self.tempfile("temp.txt")
        with open(f, "wb") as w:
            w.write(test_string.encode("latin-1"))

        with open(f, "rb") as r:
            t = EpsImagePlugin.PSFile(r)
            self._test_readline(t, ending)

    def test_readline(self):
        # check all the freaking line endings possible from the spec
        # test_string = u'something\r\nelse\n\rbaz\rbif\n'
        line_endings = ["\r\n", "\n", "\n\r", "\r"]
        strings = ["something", "else", "baz", "bif"]

        for ending in line_endings:
            s = ending.join(strings)
            self._test_readline_io_psfile(s, ending)
            self._test_readline_file_psfile(s, ending)

    def test_open_eps(self):
        # https://github.com/python-pillow/Pillow/issues/1104
        # Arrange
        FILES = [
            "Tests/images/illu10_no_preview.eps",
            "Tests/images/illu10_preview.eps",
            "Tests/images/illuCS6_no_preview.eps",
            "Tests/images/illuCS6_preview.eps",
        ]

        # Act / Assert
        for filename in FILES:
            with Image.open(filename) as img:
                self.assertEqual(img.mode, "RGB")

    @unittest.skipUnless(HAS_GHOSTSCRIPT, "Ghostscript not available")
    def test_emptyline(self):
        # Test file includes an empty line in the header data
        emptyline_file = "Tests/images/zero_bb_emptyline.eps"

        with Image.open(emptyline_file) as image:
            image.load()
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (460, 352))
        self.assertEqual(image.format, "EPS")
