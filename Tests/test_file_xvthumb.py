from helper import unittest, PillowTestCase

from PIL import XVThumbImagePlugin


class TestFileXVThumb(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          XVThumbImagePlugin.XVThumbImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
