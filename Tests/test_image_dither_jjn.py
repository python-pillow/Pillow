"""Jarvis-Judice-Ninke error diffusion for bilevel and palette images."""

from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper

# The JJN kernel has twelve forward neighbors and is normalized by 48.
TAPS = (
    (1, 0, 7),
    (2, 0, 5),
    (-2, 1, 3),
    (-1, 1, 5),
    (0, 1, 7),
    (1, 1, 5),
    (2, 1, 3),
    (-2, 2, 1),
    (-1, 2, 3),
    (0, 2, 5),
    (1, 2, 3),
    (2, 2, 1),
)


def _expected_bilevel(values: list[int], size: tuple[int, int]) -> list[int]:
    width, height = size
    errors = [[0] * width for _ in range(3)]
    output: list[int] = []

    for y in range(height):
        for x in range(width):
            weighted_error = errors[y % 3][x]
            correction = abs(weighted_error) // 48
            if weighted_error < 0:
                correction = -correction
            value = max(0, min(255, values[y * width + x] + correction))
            color = 255 if value > 128 else 0
            output.append(color)

            for dx, dy, weight in TAPS:
                xx, yy = x + dx, y + dy
                if 0 <= xx < width and yy < height:
                    errors[yy % 3][xx] += (value - color) * weight

        errors[y % 3] = [0] * width

    return output


@pytest.mark.parametrize("size", [(1, 1), (1, 9), (9, 1), (3, 3), (13, 11)])
@pytest.mark.parametrize("mode", ["L", "RGB"])
def test_jjn_bilevel_matches_diffusion_kernel(mode: str, size: tuple[int, int]) -> None:
    width, height = size
    values = [(x * 37 + y * 29 + 65) % 256 for y in range(height) for x in range(width)]
    if mode == "RGB":
        im = Image.new("RGB", size)
        im.putdata([(v, v, v) for v in values])
    else:
        im = Image.new("L", size)
        im.putdata(values)

    result = im.convert("1", dither=Image.Dither.JARVIS_JUDICE_NINKE)

    assert result.mode == "1"
    assert list(result.getdata()) == _expected_bilevel(values, size)


def test_jjn_palette_differs_from_floyd_steinberg() -> None:
    size = (33, 15)
    im = Image.new("RGB", size)
    pixels = [
        ((x * 7 + y * 11) % 256,) * 3 for y in range(size[1]) for x in range(size[0])
    ]
    im.putdata(pixels)
    palette = Image.new("P", (1, 1))
    palette.putpalette((0, 0, 0, 255, 255, 255))

    jjn = im.quantize(palette=palette, dither=Image.Dither.JARVIS_JUDICE_NINKE)
    floyd = im.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)

    assert jjn.mode == "P"
    assert set(jjn.getdata()) <= {0, 1}
    assert jjn.tobytes() != floyd.tobytes()


def test_jjn_hopper_reference_image() -> None:
    # Compare with a checked-in reference image, not the Python diffusion model.
    source = hopper("RGB").crop((24, 24, 56, 56))
    result = source.convert("1", dither=Image.Dither.JARVIS_JUDICE_NINKE)
    with Image.open("Tests/images/hopper_jjn.pbm") as expected:
        assert_image_equal(result, expected)


def test_jjn_empty_image() -> None:
    assert Image.new("L", (0, 0)).convert(
        "1", dither=Image.Dither.JARVIS_JUDICE_NINKE
    ).size == (0, 0)
