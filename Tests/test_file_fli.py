from helper import unittest, PillowTestCase, tearDownModule

from PIL import Image

# sample ppm stream
file = "Tests/images/lena.fli"
data = open(file, "rb").read()


class TestFileFli(PillowTestCase):

    def test_sanity(self):
        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "FLI")


if __name__ == '__main__':
    unittest.main()

# End of file
