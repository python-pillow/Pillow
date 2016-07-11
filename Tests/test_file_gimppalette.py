from helper import unittest, PillowTestCase

from PIL.GimpPaletteFile import GimpPaletteFile


class TestImage(PillowTestCase):

    def test_sanity(self):
        with open('Tests/images/test.gpl', 'rb') as fp:
            GimpPaletteFile(fp)

        with open('Tests/images/hopper.jpg', 'rb') as fp:
            self.assertRaises(SyntaxError, lambda: GimpPaletteFile(fp))

        with open('Tests/images/bad_palette_file.gpl', 'rb') as fp:
            self.assertRaises(SyntaxError, lambda: GimpPaletteFile(fp))

        with open('Tests/images/bad_palette_entry.gpl', 'rb') as fp:
            self.assertRaises(ValueError, lambda: GimpPaletteFile(fp))

    def test_get_palette(self):
        # Arrange
        with open('Tests/images/custom_gimp_palette.gpl', 'rb') as fp:
            palette_file = GimpPaletteFile(fp)

        # Act
        palette, mode = palette_file.getpalette()

        # Assert
        self.assertEqual(mode, "RGB")


if __name__ == '__main__':
    unittest.main()
