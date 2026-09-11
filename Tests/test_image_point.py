from __future__ import annotations

import pytest

from .helper import assert_image_equal, hopper


def test_sanity() -> None:
    im = hopper()

    with pytest.raises(ValueError):
        im.point(list(range(256)))
    im.point(list(range(256)) * 3)
    im.point(lambda x: x)
    im.point(lambda x: x * 1.2)

    im = im.convert("I")
    with pytest.raises(ValueError):
        im.point(list(range(256)))
    im.point(lambda x: x * 1)
    im.point(lambda x: x + 1)
    im.point(lambda x: x - 1)
    im.point(lambda x: x * 1 + 1)
    im.point(lambda x: 0.1 + 0.2 * x)
    im.point(lambda x: -x)
    im.point(lambda x: x - 0.5)
    im.point(lambda x: 1 - x / 2)
    im.point(lambda x: (2 + x) / 3)
    im.point(lambda x: 0.5)
    im.point(lambda x: x / 1)
    im.point(lambda x: x + x)
    with pytest.raises(TypeError):
        im.point(lambda x: x * x)
    with pytest.raises(TypeError):
        im.point(lambda x: x / x)
    with pytest.raises(TypeError):
        im.point(lambda x: 1 / x)
    with pytest.raises(TypeError):
        im.point(lambda x: x // 2)


@pytest.mark.parametrize("mode", ("LA", "RGBA", "CMYK"))
def test_multiband(mode: str) -> None:
    # Exercises im_point_2x8_2x8 (2 bands) and im_point_4x8_4x8 (4 bands)
    im = hopper(mode)
    lut = [(x + 1) % 256 for x in range(256)] * len(im.getbands())
    out = im.point(lut)

    assert out.mode == mode
    assert isinstance(px := im.getpixel((0, 0)), tuple)  # Placate mypy
    expected_px = tuple((v + 1) % 256 for v in px)
    assert out.getpixel((0, 0)) == expected_px


def test_16bit_lut() -> None:
    """Tests for 16 bit -> 8 bit lut for converting I->L images
    see https://github.com/python-pillow/Pillow/issues/440
    """
    im = hopper("I")
    im.point(list(range(256)) * 256, "L")


def test_f_lut() -> None:
    """Tests for floating point lut of 8bit gray image"""
    im = hopper("L")
    lut = [0.5 * float(x) for x in range(256)]

    out = im.point(lut, "F")

    int_lut = [x // 2 for x in range(256)]
    assert_image_equal(out.convert("L"), im.point(int_lut, "L"))


def test_f_mode() -> None:
    im = hopper("F")
    with pytest.raises(ValueError):
        im.point([])
