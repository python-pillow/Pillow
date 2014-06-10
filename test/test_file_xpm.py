from helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
file = "Images/lena.xpm"
data = open(file, "rb").read()


class TestFileXpm(PillowTestCase):

    def test_sanity(self):
        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "XPM")


if __name__ == '__main__':
    unittest.main()

# End of file
