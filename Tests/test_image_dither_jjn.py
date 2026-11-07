"""Jarvis-Judice-Ninke error diffusion for bilevel and palette images."""

from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper


@pytest.mark.parametrize("size", [(1, 1), (1, 9), (9, 1), (3, 3), (13, 11)])
@pytest.mark.parametrize("mode", ["L", "RGB"])
@pytest.mark.parametrize("value", [0, 255])
def test_jjn_bilevel_solid_image(mode: str, size: tuple[int, int], value: int) -> None:
    im = Image.new(mode, size, (value,) * 3 if mode == "RGB" else value)
    result = im.convert("1", dither=Image.Dither.JARVIS_JUDICE_NINKE)
    assert_image_equal(result, Image.new("1", size, value))


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
    source = hopper("RGB").crop((24, 24, 56, 56))
    result = source.convert("1", dither=Image.Dither.JARVIS_JUDICE_NINKE)
    with Image.open("Tests/images/hopper_jjn.pbm") as expected:
        assert_image_equal(result, expected)


def test_jjn_empty_image() -> None:
    assert Image.new("L", (0, 0)).convert(
        "1", dither=Image.Dither.JARVIS_JUDICE_NINKE
    ).size == (0, 0)
