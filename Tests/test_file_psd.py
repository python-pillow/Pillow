from helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
file = "Tests/images/hopper.psd"
data = open(file, "rb").read()


class TestImagePsd(PillowTestCase):

    def test_sanity(self):
        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "PSD")


if __name__ == '__main__':
    unittest.main()

# End of file
