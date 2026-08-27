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
        with pytest.raises(SyntaxError, match="bad palette file"):
            GimpPaletteFile(fp)

    with open("Tests/images/bad_palette_entry.gpl", "rb") as fp:
        with pytest.raises(ValueError, match="bad palette entry"):
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


def test_frombytes() -> None:
    # Test that __init__ stops reading after 260 lines
    with open("Tests/images/custom_gimp_palette.gpl", "rb") as fp:
        custom_data = fp.read()
    custom_data += b"#\n" * 300 + b"  0   0   0     Index 12"
    b = BytesIO(custom_data)
    palette = GimpPaletteFile(b)
    assert len(palette.palette) / 3 == 8

    # Test that __init__ only reads 256 entries
    with open("Tests/images/full_gimp_palette.gpl", "rb") as fp:
        full_data = fp.read()
    data = full_data.replace(b"#\n", b"") + b"  0   0   0     Index 256"
    b = BytesIO(data)
    palette = GimpPaletteFile(b)
    assert len(palette.palette) / 3 == 256

    # Test that frombytes() can read beyond that
    palette = GimpPaletteFile.frombytes(data)
    assert len(palette.palette) / 3 == 257

    # Test that __init__ raises an error if a comment is too long
    data = full_data[:-1] + b"a" * 100
    b = BytesIO(data)
    with pytest.raises(SyntaxError, match="bad palette file"):
        palette = GimpPaletteFile(b)

    # Test that frombytes() can read the data regardless
    palette = GimpPaletteFile.frombytes(data)
    assert len(palette.palette) / 3 == 256
