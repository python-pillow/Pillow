from __future__ import annotations

import pytest

from PIL import Image

from .helper import hopper


@pytest.mark.parametrize(
    "size, source, expected",
    [
        ((1, 7), "007f8081ff64c8", "0000ffffff00ff"),
        ((2, 5), "7f80817e03fc6496c832", "00ffff0000ff00ffff00"),
        ((3, 3), "7f80817e7f80817e7f", "00ffff0000ffff0000"),
        (
            (7, 3),
            "285078a0c8f064285078a0c8f064285078a0c8f064",
            "0000ffffffff00000000ffffff000000ffffffff00",
        ),
        (
            (9, 2),
            "01fe3f40417f8081c001fe3f40417f8081c0",
            "00ff000000ff00ffff00ff000000ff0000ff",
        ),
        # A negative error must round down: (254 - 255) / 8 becomes -1.
        ((2, 1), "fe80", "ff00"),
    ],
)
def test_atkinson(size: tuple[int, int], source: str, expected: str) -> None:
    data = bytes.fromhex(source)
    im = Image.frombytes("L", size, data)
    result = im.convert("1", dither=Image.Dither.ATKINSON)
    assert result.mode == "1"
    assert result.size == size
    assert result.tobytes("raw", "L") == bytes.fromhex(expected)
    assert result.convert("L").tobytes() == bytes.fromhex(expected)
    assert im.tobytes() == data


@pytest.mark.parametrize("value", range(256))
def test_atkinson_threshold(value: int) -> None:
    im = Image.new("L", (1, 1), value)
    result = im.convert("1", dither=Image.Dither.ATKINSON)
    assert result.getpixel((0, 0)) == (255 if value >= 128 else 0)


@pytest.mark.parametrize("size", [(0, 0), (0, 1), (1, 0), (0, 10), (10, 0)])
def test_atkinson_empty(size: tuple[int, int]) -> None:
    im = Image.new("L", size)
    result = im.convert("1", dither=Image.Dither.ATKINSON)
    assert result.size == size
    assert result.tobytes() == b""


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "RGBX", "LA", "P", "PA", "1"])
def test_atkinson_modes(mode: str) -> None:
    im = hopper(mode)
    original = im.tobytes()
    result = im.convert("1", dither=Image.Dither.ATKINSON)
    expected = im.convert("L").convert("1", dither=Image.Dither.ATKINSON)
    assert result.tobytes() == expected.tobytes()
    assert im.tobytes() == original


@pytest.mark.parametrize("mode", ["P", "PA"])
@pytest.mark.parametrize("palette", [Image.Palette.WEB, Image.Palette.ADAPTIVE])
def test_atkinson_palette(mode: str, palette: Image.Palette) -> None:
    with pytest.raises(ValueError, match="Atkinson dithering is only supported"):
        hopper().convert(mode, dither=Image.Dither.ATKINSON, palette=palette)


def test_atkinson_quantize_palette() -> None:
    palette = hopper("P")
    with pytest.raises(ValueError, match="Atkinson dithering is only supported"):
        hopper().quantize(palette=palette, dither=Image.Dither.ATKINSON)


def test_atkinson_row_padding() -> None:
    im = Image.frombytes(
        "L", (9, 2), bytes.fromhex("01fe3f40417f8081c001fe3f40417f8081c0")
    )
    result = im.convert("1", dither=Image.Dither.ATKINSON)
    assert result.tobytes() == bytes.fromhex("45804480")
