from helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
# created as an export of a palette image from Gimp2.6
# save as...-> hopper.fli, default options.
test_file = "Tests/images/hopper.fli"
data = open(test_file, "rb").read()


class TestFileFli(PillowTestCase):

    def test_sanity(self):
        im = Image.open(test_file)
        im.load()
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "FLI")


if __name__ == '__main__':
    unittest.main()

# End of file
