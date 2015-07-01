from helper import unittest, PillowTestCase

from PIL.GimpPaletteFile import GimpPaletteFile


class TestImage(PillowTestCase):

    def test_sanity(self):
        with open('Tests/images/test.gpl', 'rb') as fp:
            GimpPaletteFile(fp)

        with open('Tests/images/hopper.jpg', 'rb') as fp:
            self.assertRaises(SyntaxError, lambda: GimpPaletteFile(fp))


if __name__ == '__main__':
    unittest.main()

# End of file
