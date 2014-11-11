from helper import unittest, PillowTestCase, hopper

from PIL import Image
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


if __name__ == '__main__':
    unittest.main()

# End of file
