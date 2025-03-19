from __future__ import annotations

import pytest

from PIL.GimpPaletteFile import GimpPaletteFile


def test_sanity() -> None:
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


def test_large_file_is_truncated() -> None:
    original_max_file_size = GimpPaletteFile._max_file_size
    try:
        GimpPaletteFile._max_file_size = 100
        with open("Tests/images/custom_gimp_palette.gpl", "rb") as fp:
            with pytest.warns(UserWarning):
                GimpPaletteFile(fp)
    finally:
        GimpPaletteFile._max_file_size = original_max_file_size


def test_get_palette() -> None:
    # Arrange
    with open("Tests/images/custom_gimp_palette.gpl", "rb") as fp:
        palette_file = GimpPaletteFile(fp)

    # Act
    palette, mode = palette_file.getpalette()

    # Assert
    expected_palette: list[int] = []
    for color in (
        (0, 0, 0),
        (65, 38, 30),
        (103, 62, 49),
        (79, 73, 72),
        (114, 101, 97),
        (208, 127, 100),
        (151, 144, 142),
        (221, 207, 199),
    ):
        expected_palette += color
    assert palette == bytes(expected_palette)
    assert mode == "RGB"
    assert len(palette) / 3 == 8
