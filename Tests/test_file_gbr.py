from helper import unittest, PillowTestCase

from PIL import GbrImagePlugin


class TestFileGbr(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: GbrImagePlugin.GbrImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
