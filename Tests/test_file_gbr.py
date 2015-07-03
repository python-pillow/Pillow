from helper import unittest, PillowTestCase

from PIL import GbrImagePlugin


class TestFileGbr(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: GbrImagePlugin.GbrImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()

# End of file
