import pytest

from PIL.GimpPaletteFile import GimpPaletteFile


def test_sanity():
    with open("Tests/images/test.gpl", "rb") as fp:
        GimpPaletteFile(fp)

    with open("Tests/images/hopper.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            GimpPaletteFile(fp)

    with open("Tests/images/bad_palette_file.gpl", "rb") as fp:
        with pytest.raises(SyntaxError):
            GimpPaletteFile(fp)

    with open("Tests/images/bad_palette_entry.gpl", "rb") as fp:
        with pytest.raises(ValueError):
            GimpPaletteFile(fp)


def test_get_palette():
    # Arrange
    with open("Tests/images/custom_gimp_palette.gpl", "rb") as fp:
        palette_file = GimpPaletteFile(fp)

    # Act
    palette, mode = palette_file.getpalette()

    # Assert
    assert mode == "RGB"
