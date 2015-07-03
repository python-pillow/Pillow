from helper import unittest, PillowTestCase

from PIL import MicImagePlugin


class TestFileMic(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: MicImagePlugin.MicImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
