from __future__ import annotations

import pytest

from PIL import Image

from .helper import hopper


def test_sanity() -> None:
    bbox = hopper().getbbox()
    assert isinstance(bbox, tuple)


def test_bbox() -> None:
    def check(im: Image.Image, fill_color: int | tuple[int, ...]) -> None:
        assert im.getbbox() is None

        im.paste(fill_color, (10, 25, 90, 75))
        assert im.getbbox() == (10, 25, 90, 75)

        im.paste(fill_color, (25, 10, 75, 90))
        assert im.getbbox() == (10, 10, 90, 90)

        im.paste(fill_color, (-10, -10, 110, 110))
        assert im.getbbox() == (0, 0, 100, 100)

    # 8-bit mode
    im = Image.new("L", (100, 100), 0)
    check(im, 255)

    # 32-bit mode
    im = Image.new("RGB", (100, 100), 0)
    check(im, 255)

    for mode in ("RGBA", "RGBa"):
        for rgba_color in ((0, 0, 0, 0), (127, 127, 127, 0), (255, 255, 255, 0)):
            im = Image.new(mode, (100, 100), rgba_color)
            check(im, (255, 255, 255, 255))

    for mode in ("La", "LA", "PA"):
        for color in ((0, 0), (127, 0), (255, 0)):
            im = Image.new(mode, (100, 100), color)
            check(im, (255, 255))


@pytest.mark.parametrize("mode", ("L", "RGB", "RGBA", "I", "F"))
@pytest.mark.parametrize(
    "box",
    (
        (0, 0, 1, 1),  # single pixel, top-left
        (99, 0, 100, 1),  # single pixel, top-right
        (0, 99, 1, 100),  # single pixel, bottom-left
        (99, 99, 100, 100),  # single pixel, bottom-right
        (0, 0, 100, 1),  # full top row
        (0, 99, 100, 100),  # full bottom row
        (0, 0, 1, 100),  # full left column
        (99, 0, 100, 100),  # full right column
        (40, 40, 60, 60),  # centred block
    ),
)
def test_bbox_edges(mode: str, box: tuple[int, int, int, int]) -> None:
    im = Image.new(mode, (100, 100), 0)
    bands = Image.getmodebands(mode)
    im.paste((255,) * bands, box)
    assert im.getbbox() == box


@pytest.mark.parametrize("mode", ("RGBA", "RGBa", "La", "LA", "PA"))
def test_bbox_alpha_only_false(mode: str) -> None:
    im = Image.new(mode, (100, 100))
    assert im.getbbox(alpha_only=False) is None

    fill_color = [1] * Image.getmodebands(mode)
    fill_color[-1] = 0
    im.paste(tuple(fill_color), (25, 25, 75, 75))
    assert im.getbbox(alpha_only=False) == (25, 25, 75, 75)

    assert im.getbbox() is None
