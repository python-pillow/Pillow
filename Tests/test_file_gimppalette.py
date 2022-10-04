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


def test_palette__has_correct_color_indexes():
    # Arrange
    with open("Tests/images/custom_gimp_palette.gpl", "rb") as fp:
        palette_file = GimpPaletteFile(fp)

    palette, mode = palette_file.getpalette()

    colors_in_test_palette = [
        (0, 0, 0),
        (65, 38, 30),
        (103, 62, 49),
        (79, 73, 72),
        (114, 101, 97),
        (208, 127, 100),
        (151, 144, 142),
        (221, 207, 199),
    ]

    for i, color in enumerate(colors_in_test_palette):
        assert tuple(palette[i * 3: i * 3 + 3]) == color


def test_palette_counts_number_of_colors_in_file():
    # Arrange
    with open("Tests/images/custom_gimp_palette.gpl", "rb") as fp:
        palette_file = GimpPaletteFile(fp)

    assert palette_file.n_colors == 8
