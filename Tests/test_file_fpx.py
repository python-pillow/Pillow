from helper import unittest, PillowTestCase

from PIL import FpxImagePlugin


class TestFileFpx(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: FpxImagePlugin.FpxImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
