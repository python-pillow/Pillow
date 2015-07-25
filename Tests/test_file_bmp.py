from helper import unittest, PillowTestCase, hopper

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

    def test_sanity(self):
        self.roundtrip(hopper())

        self.roundtrip(hopper("1"))
        self.roundtrip(hopper("L"))
        self.roundtrip(hopper("P"))
        self.roundtrip(hopper("RGB"))

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError,
                              lambda: BmpImagePlugin.BmpImageFile(fp))

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


if __name__ == '__main__':
    unittest.main()

# End of file
