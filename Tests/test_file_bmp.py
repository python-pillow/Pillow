import io

from PIL import BmpImagePlugin, Image

from .helper import PillowTestCase, hopper


class TestFileBmp(PillowTestCase):
    def roundtrip(self, im):
        outfile = self.tempfile("temp.bmp")

        im.save(outfile, "BMP")

        with Image.open(outfile) as reloaded:
            reloaded.load()
            self.assertEqual(im.mode, reloaded.mode)
            self.assertEqual(im.size, reloaded.size)
            self.assertEqual(reloaded.format, "BMP")
            self.assertEqual(reloaded.get_format_mimetype(), "image/bmp")

    def test_sanity(self):
        self.roundtrip(hopper())

        self.roundtrip(hopper("1"))
        self.roundtrip(hopper("L"))
        self.roundtrip(hopper("P"))
        self.roundtrip(hopper("RGB"))

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, BmpImagePlugin.BmpImageFile, fp)

    def test_save_to_bytes(self):
        output = io.BytesIO()
        im = hopper()
        im.save(output, "BMP")

        output.seek(0)
        with Image.open(output) as reloaded:
            self.assertEqual(im.mode, reloaded.mode)
            self.assertEqual(im.size, reloaded.size)
            self.assertEqual(reloaded.format, "BMP")

    def test_save_too_large(self):
        outfile = self.tempfile("temp.bmp")
        with Image.new("RGB", (1, 1)) as im:
            im._size = (37838, 37838)
            with self.assertRaises(ValueError):
                im.save(outfile)

    def test_dpi(self):
        dpi = (72, 72)

        output = io.BytesIO()
        with hopper() as im:
            im.save(output, "BMP", dpi=dpi)

        output.seek(0)
        with Image.open(output) as reloaded:
            self.assertEqual(reloaded.info["dpi"], dpi)

    def test_save_bmp_with_dpi(self):
        # Test for #1301
        # Arrange
        outfile = self.tempfile("temp.jpg")
        with Image.open("Tests/images/hopper.bmp") as im:

            # Act
            im.save(outfile, "JPEG", dpi=im.info["dpi"])

            # Assert
            with Image.open(outfile) as reloaded:
                reloaded.load()
                self.assertEqual(im.info["dpi"], reloaded.info["dpi"])
                self.assertEqual(im.size, reloaded.size)
                self.assertEqual(reloaded.format, "JPEG")

    def test_load_dpi_rounding(self):
        # Round up
        with Image.open("Tests/images/hopper.bmp") as im:
            self.assertEqual(im.info["dpi"], (96, 96))

        # Round down
        with Image.open("Tests/images/hopper_roundDown.bmp") as im:
            self.assertEqual(im.info["dpi"], (72, 72))

    def test_save_dpi_rounding(self):
        outfile = self.tempfile("temp.bmp")
        with Image.open("Tests/images/hopper.bmp") as im:
            im.save(outfile, dpi=(72.2, 72.2))
            with Image.open(outfile) as reloaded:
                self.assertEqual(reloaded.info["dpi"], (72, 72))

            im.save(outfile, dpi=(72.8, 72.8))
        with Image.open(outfile) as reloaded:
            self.assertEqual(reloaded.info["dpi"], (73, 73))

    def test_load_dib(self):
        # test for #1293, Imagegrab returning Unsupported Bitfields Format
        with Image.open("Tests/images/clipboard.dib") as im:
            self.assertEqual(im.format, "DIB")
            self.assertEqual(im.get_format_mimetype(), "image/bmp")

            with Image.open("Tests/images/clipboard_target.png") as target:
                self.assert_image_equal(im, target)

    def test_save_dib(self):
        outfile = self.tempfile("temp.dib")

        with Image.open("Tests/images/clipboard.dib") as im:
            im.save(outfile)

            with Image.open(outfile) as reloaded:
                self.assertEqual(reloaded.format, "DIB")
                self.assertEqual(reloaded.get_format_mimetype(), "image/bmp")
                self.assert_image_equal(im, reloaded)

    def test_rgba_bitfields(self):
        # This test image has been manually hexedited
        # to change the bitfield compression in the header from XBGR to RGBA
        with Image.open("Tests/images/rgb32bf-rgba.bmp") as im:

            # So before the comparing the image, swap the channels
            b, g, r = im.split()[1:]
            im = Image.merge("RGB", (r, g, b))

        with Image.open("Tests/images/bmp/q/rgb32bf-xbgr.bmp") as target:
            self.assert_image_equal(im, target)
