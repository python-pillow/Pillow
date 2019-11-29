from PIL.GimpPaletteFile import GimpPaletteFile

from .helper import PillowTestCase


class TestImage(PillowTestCase):
    def test_sanity(self):
        with open("Tests/images/test.gpl", "rb") as fp:
            GimpPaletteFile(fp)

        with open("Tests/images/hopper.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, GimpPaletteFile, fp)

        with open("Tests/images/bad_palette_file.gpl", "rb") as fp:
            self.assertRaises(SyntaxError, GimpPaletteFile, fp)

        with open("Tests/images/bad_palette_entry.gpl", "rb") as fp:
            self.assertRaises(ValueError, GimpPaletteFile, fp)

    def test_get_palette(self):
        # Arrange
        with open("Tests/images/custom_gimp_palette.gpl", "rb") as fp:
            palette_file = GimpPaletteFile(fp)

        # Act
        palette, mode = palette_file.getpalette()

        # Assert
        self.assertEqual(mode, "RGB")
