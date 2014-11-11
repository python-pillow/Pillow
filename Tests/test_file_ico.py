from helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
TEST_ICO_FILE = "Tests/images/hopper.ico"
TEST_DATA = open(TEST_ICO_FILE, "rb").read()


class TestFileIco(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_ICO_FILE)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (16, 16))
        self.assertEqual(im.format, "ICO")


if __name__ == '__main__':
    unittest.main()

# End of file
