from helper import unittest, PillowTestCase, hopper, fromstring, tostring

from io import BytesIO

from PIL import Image
from PIL import ImageFile
from PIL import EpsImagePlugin


codecs = dir(Image.core)

# save original block sizes
MAXBLOCK = ImageFile.MAXBLOCK
SAFEBLOCK = ImageFile.SAFEBLOCK


class TestImageFile(PillowTestCase):

    def test_parser(self):

        def roundtrip(format):

            im = hopper("L").resize((1000, 1000))
            if format in ("MSP", "XBM"):
                im = im.convert("1")

            test_file = BytesIO()

            im.copy().save(test_file, format)

            data = test_file.getvalue()

            parser = ImageFile.Parser()
            parser.feed(data)
            imOut = parser.close()

            return im, imOut

        self.assert_image_equal(*roundtrip("BMP"))
        im1, im2 = roundtrip("GIF")
        self.assert_image_similar(im1.convert('P'), im2, 1)
        self.assert_image_equal(*roundtrip("IM"))
        self.assert_image_equal(*roundtrip("MSP"))
        if "zip_encoder" in codecs:
            try:
                # force multiple blocks in PNG driver
                ImageFile.MAXBLOCK = 8192
                self.assert_image_equal(*roundtrip("PNG"))
            finally:
                ImageFile.MAXBLOCK = MAXBLOCK
        self.assert_image_equal(*roundtrip("PPM"))
        self.assert_image_equal(*roundtrip("TIFF"))
        self.assert_image_equal(*roundtrip("XBM"))
        self.assert_image_equal(*roundtrip("TGA"))
        self.assert_image_equal(*roundtrip("PCX"))

        if EpsImagePlugin.has_ghostscript():
            im1, im2 = roundtrip("EPS")
            # This test fails on Ubuntu 12.04, PPC (Bigendian) It
            # appears to be a ghostscript 9.05 bug, since the
            # ghostscript rendering is wonky and the file is identical
            # to that written on ubuntu 12.04 x64
            # md5sum: ba974835ff2d6f3f2fd0053a23521d4a

            # EPS comes back in RGB:
            self.assert_image_similar(im1, im2.convert('L'), 20)

        if "jpeg_encoder" in codecs:
            im1, im2 = roundtrip("JPEG")  # lossy compression
            self.assert_image(im1, im2.mode, im2.size)

        self.assertRaises(IOError, lambda: roundtrip("PDF"))

    def test_ico(self):
        with open('Tests/images/python.ico', 'rb') as f:
            data = f.read()
        p = ImageFile.Parser()
        p.feed(data)
        self.assertEqual((48, 48), p.image.size)

    def test_safeblock(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        im1 = hopper()

        try:
            ImageFile.SAFEBLOCK = 1
            im2 = fromstring(tostring(im1, "PNG"))
        finally:
            ImageFile.SAFEBLOCK = SAFEBLOCK

        self.assert_image_equal(im1, im2)

    def test_raise_ioerror(self):
        self.assertRaises(IOError, lambda: ImageFile.raise_ioerror(1))

    def test_truncated_with_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        im = Image.open("Tests/images/truncated_image.png")
        with self.assertRaises(IOError):
            im.load()

    def test_truncated_without_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        im = Image.open("Tests/images/truncated_image.png")

        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            im.load()
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

    def test_broken_datastream_with_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        im = Image.open("Tests/images/broken_data_stream.png")
        with self.assertRaises(IOError):
            im.load()

    def test_broken_datastream_without_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        im = Image.open("Tests/images/broken_data_stream.png")

        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            im.load()
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

if __name__ == '__main__':
    unittest.main()

# End of file
