from test.helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
file = "Images/lena.ico"
data = open(file, "rb").read()


class TestFileIco(PillowTestCase):

    def test_sanity(self):
        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (16, 16))
        self.assertEqual(im.format, "ICO")


if __name__ == '__main__':
    unittest.main()

# End of file
