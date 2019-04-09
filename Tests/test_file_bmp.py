from .helper import PillowTestCase, hopper

from PIL import Image, BmpImagePlugin
import io


class TestFileBmp(PillowTestCase):

    def roundtrip(self, im):
        outfile = self.tempfile("temp.bmp")

        im.save(outfile, 'BMP')

        reloaded = Image.open(outfile)
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
            self.assertRaises(SyntaxError,
                              BmpImagePlugin.BmpImageFile, fp)

    def test_save_to_bytes(self):
        output = io.BytesIO()
        im = hopper()
        im.save(output, "BMP")

        output.seek(0)
        reloaded = Image.open(output)

        self.assertEqual(im.mode, reloaded.mode)
        self.assertEqual(im.size, reloaded.size)
        self.assertEqual(reloaded.format, "BMP")

    def test_dpi(self):
        dpi = (72, 72)

        output = io.BytesIO()
        im = hopper()
        im.save(output, "BMP", dpi=dpi)

        output.seek(0)
        reloaded = Image.open(output)

        self.assertEqual(reloaded.info["dpi"], dpi)

    def test_save_bmp_with_dpi(self):
        # Test for #1301
        # Arrange
        outfile = self.tempfile("temp.jpg")
        im = Image.open("Tests/images/hopper.bmp")

        # Act
        im.save(outfile, 'JPEG', dpi=im.info['dpi'])

        # Assert
        reloaded = Image.open(outfile)
        reloaded.load()
        self.assertEqual(im.info['dpi'], reloaded.info['dpi'])
        self.assertEqual(im.size, reloaded.size)
        self.assertEqual(reloaded.format, "JPEG")

    def test_load_dpi_rounding(self):
        # Round up
        im = Image.open('Tests/images/hopper.bmp')
        self.assertEqual(im.info["dpi"], (96, 96))

        # Round down
        im = Image.open('Tests/images/hopper_roundDown.bmp')
        self.assertEqual(im.info["dpi"], (72, 72))

    def test_save_dpi_rounding(self):
        outfile = self.tempfile("temp.bmp")
        im = Image.open('Tests/images/hopper.bmp')

        im.save(outfile, dpi=(72.2, 72.2))
        reloaded = Image.open(outfile)
        self.assertEqual(reloaded.info["dpi"], (72, 72))

        im.save(outfile, dpi=(72.8, 72.8))
        reloaded = Image.open(outfile)
        self.assertEqual(reloaded.info["dpi"], (73, 73))

    def test_load_dib(self):
        # test for #1293, Imagegrab returning Unsupported Bitfields Format
        im = Image.open('Tests/images/clipboard.dib')
        self.assertEqual(im.format, "DIB")
        self.assertEqual(im.get_format_mimetype(), "image/bmp")

        target = Image.open('Tests/images/clipboard_target.png')
        self.assert_image_equal(im, target)

    def test_save_dib(self):
        outfile = self.tempfile("temp.dib")

        im = Image.open('Tests/images/clipboard.dib')
        im.save(outfile)

        reloaded = Image.open(outfile)
        self.assertEqual(reloaded.format, "DIB")
        self.assertEqual(reloaded.get_format_mimetype(), "image/bmp")
        self.assert_image_equal(im, reloaded)

    def test_rgba_bitfields(self):
        # This test image has been manually hexedited
        # to change the bitfield compression in the header from XBGR to RGBA
        im = Image.open("Tests/images/rgb32bf-rgba.bmp")

        # So before the comparing the image, swap the channels
        b, g, r = im.split()[1:]
        im = Image.merge("RGB", (r, g, b))

        target = Image.open("Tests/images/bmp/q/rgb32bf-xbgr.bmp")
        self.assert_image_equal(im, target)
