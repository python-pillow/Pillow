from __future__ import annotations

from io import BytesIO

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


@pytest.mark.parametrize(
    "filename, size", (("custom_gimp_palette.gpl", 8), ("full_gimp_palette.gpl", 256))
)
def test_get_palette(filename: str, size: int) -> None:
    # Arrange
    with open("Tests/images/" + filename, "rb") as fp:
        palette_file = GimpPaletteFile(fp)

    # Act
    palette, mode = palette_file.getpalette()

    # Assert
    assert mode == "RGB"
    assert len(palette) / 3 == size


def test_palette_limit() -> None:
    with open("Tests/images/full_gimp_palette.gpl", "rb") as fp:
        data = fp.read()

    # Test that __init__ only reads 256 entries
    data = data.replace(b"#\n", b"") + b"  0   0   0     Index 256"
    b = BytesIO(data)
    palette = GimpPaletteFile(b)
    assert len(palette.palette) / 3 == 256
