import unittest
from io import BytesIO

from PIL import EpsImagePlugin, Image, ImageFile

from .helper import PillowTestCase, fromstring, hopper, tostring

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


codecs = dir(Image.core)

# save original block sizes
MAXBLOCK = ImageFile.MAXBLOCK
SAFEBLOCK = ImageFile.SAFEBLOCK


class TestImageFile(PillowTestCase):
    def test_parser(self):
        def roundtrip(format):

            im = hopper("L").resize((1000, 1000), Image.NEAREST)
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
        self.assert_image_similar(im1.convert("P"), im2, 1)
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
            self.assert_image_similar(im1, im2.convert("L"), 20)

        if "jpeg_encoder" in codecs:
            im1, im2 = roundtrip("JPEG")  # lossy compression
            self.assert_image(im1, im2.mode, im2.size)

        self.assertRaises(IOError, roundtrip, "PDF")

    def test_ico(self):
        with open("Tests/images/python.ico", "rb") as f:
            data = f.read()
        with ImageFile.Parser() as p:
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
        self.assertRaises(IOError, ImageFile.raise_ioerror, 1)

    def test_raise_typeerror(self):
        with self.assertRaises(TypeError):
            parser = ImageFile.Parser()
            parser.feed(1)

    def test_negative_stride(self):
        with open("Tests/images/raw_negative_stride.bin", "rb") as f:
            input = f.read()
        p = ImageFile.Parser()
        p.feed(input)
        with self.assertRaises(IOError):
            p.close()

    def test_truncated_with_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        with Image.open("Tests/images/truncated_image.png") as im:
            with self.assertRaises(IOError):
                im.load()

            # Test that the error is raised if loaded a second time
            with self.assertRaises(IOError):
                im.load()

    def test_truncated_without_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        with Image.open("Tests/images/truncated_image.png") as im:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            try:
                im.load()
            finally:
                ImageFile.LOAD_TRUNCATED_IMAGES = False

    def test_broken_datastream_with_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        with Image.open("Tests/images/broken_data_stream.png") as im:
            with self.assertRaises(IOError):
                im.load()

    def test_broken_datastream_without_errors(self):
        if "zip_encoder" not in codecs:
            self.skipTest("PNG (zlib) encoder not available")

        with Image.open("Tests/images/broken_data_stream.png") as im:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            try:
                im.load()
            finally:
                ImageFile.LOAD_TRUNCATED_IMAGES = False


class MockPyDecoder(ImageFile.PyDecoder):
    def decode(self, buffer):
        # eof
        return -1, 0


xoff, yoff, xsize, ysize = 10, 20, 100, 100


class MockImageFile(ImageFile.ImageFile):
    def _open(self):
        self.rawmode = "RGBA"
        self.mode = "RGBA"
        self._size = (200, 200)
        self.tile = [("MOCK", (xoff, yoff, xoff + xsize, yoff + ysize), 32, None)]


class TestPyDecoder(PillowTestCase):
    def get_decoder(self):
        decoder = MockPyDecoder(None)

        def closure(mode, *args):
            decoder.__init__(mode, *args)
            return decoder

        Image.register_decoder("MOCK", closure)
        return decoder

    def test_setimage(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        d = self.get_decoder()

        im.load()

        self.assertEqual(d.state.xoff, xoff)
        self.assertEqual(d.state.yoff, yoff)
        self.assertEqual(d.state.xsize, xsize)
        self.assertEqual(d.state.ysize, ysize)

        self.assertRaises(ValueError, d.set_as_raw, b"\x00")

    def test_extents_none(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [("MOCK", None, 32, None)]
        d = self.get_decoder()

        im.load()

        self.assertEqual(d.state.xoff, 0)
        self.assertEqual(d.state.yoff, 0)
        self.assertEqual(d.state.xsize, 200)
        self.assertEqual(d.state.ysize, 200)

    def test_negsize(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [("MOCK", (xoff, yoff, -10, yoff + ysize), 32, None)]
        self.get_decoder()

        self.assertRaises(ValueError, im.load)

        im.tile = [("MOCK", (xoff, yoff, xoff + xsize, -10), 32, None)]
        self.assertRaises(ValueError, im.load)

    def test_oversize(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [("MOCK", (xoff, yoff, xoff + xsize + 100, yoff + ysize), 32, None)]
        self.get_decoder()

        self.assertRaises(ValueError, im.load)

        im.tile = [("MOCK", (xoff, yoff, xoff + xsize, yoff + ysize + 100), 32, None)]
        self.assertRaises(ValueError, im.load)

    def test_no_format(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        self.assertIsNone(im.format)
        self.assertIsNone(im.get_format_mimetype())

    def test_exif_jpeg(self):
        with Image.open("Tests/images/exif-72dpi-int.jpg") as im:  # Little endian
            exif = im.getexif()
            self.assertNotIn(258, exif)
            self.assertIn(40960, exif)
            self.assertEqual(exif[40963], 450)
            self.assertEqual(exif[11], "gThumb 3.0.1")

            out = self.tempfile("temp.jpg")
            exif[258] = 8
            del exif[40960]
            exif[40963] = 455
            exif[11] = "Pillow test"
            im.save(out, exif=exif)
        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            self.assertEqual(reloaded_exif[258], 8)
            self.assertNotIn(40960, exif)
            self.assertEqual(reloaded_exif[40963], 455)
            self.assertEqual(exif[11], "Pillow test")

        with Image.open("Tests/images/no-dpi-in-exif.jpg") as im:  # Big endian
            exif = im.getexif()
            self.assertNotIn(258, exif)
            self.assertIn(40962, exif)
            self.assertEqual(exif[40963], 200)
            self.assertEqual(exif[305], "Adobe Photoshop CC 2017 (Macintosh)")

            out = self.tempfile("temp.jpg")
            exif[258] = 8
            del exif[34665]
            exif[40963] = 455
            exif[305] = "Pillow test"
            im.save(out, exif=exif)
        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            self.assertEqual(reloaded_exif[258], 8)
            self.assertNotIn(40960, exif)
            self.assertEqual(reloaded_exif[40963], 455)
            self.assertEqual(exif[305], "Pillow test")

    @unittest.skipIf(
        not HAVE_WEBP or not _webp.HAVE_WEBPANIM,
        "WebP support not installed with animation",
    )
    def test_exif_webp(self):
        with Image.open("Tests/images/hopper.webp") as im:
            exif = im.getexif()
            self.assertEqual(exif, {})

            out = self.tempfile("temp.webp")
            exif[258] = 8
            exif[40963] = 455
            exif[305] = "Pillow test"

            def check_exif():
                with Image.open(out) as reloaded:
                    reloaded_exif = reloaded.getexif()
                    self.assertEqual(reloaded_exif[258], 8)
                    self.assertEqual(reloaded_exif[40963], 455)
                    self.assertEqual(exif[305], "Pillow test")

            im.save(out, exif=exif)
            check_exif()
            im.save(out, exif=exif, save_all=True)
            check_exif()

    def test_exif_png(self):
        with Image.open("Tests/images/exif.png") as im:
            exif = im.getexif()
            self.assertEqual(exif, {274: 1})

            out = self.tempfile("temp.png")
            exif[258] = 8
            del exif[274]
            exif[40963] = 455
            exif[305] = "Pillow test"
            im.save(out, exif=exif)

        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            self.assertEqual(reloaded_exif, {258: 8, 40963: 455, 305: "Pillow test"})

    def test_exif_interop(self):
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()
            self.assertEqual(
                exif.get_ifd(0xA005), {1: "R98", 2: b"0100", 4097: 2272, 4098: 1704}
            )
