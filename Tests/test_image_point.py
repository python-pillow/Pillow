import pytest

from .helper import assert_image_equal, hopper


def test_sanity():
    im = hopper()

    with pytest.raises(ValueError):
        im.point(list(range(256)))
    im.point(list(range(256)) * 3)
    im.point(lambda x: x)

    im = im.convert("I")
    with pytest.raises(ValueError):
        im.point(list(range(256)))
    im.point(lambda x: x * 1)
    im.point(lambda x: x + 1)
    im.point(lambda x: x * 1 + 1)
    with pytest.raises(TypeError):
        im.point(lambda x: x - 1)
    with pytest.raises(TypeError):
        im.point(lambda x: x / 1)


def test_16bit_lut():
    """Tests for 16 bit -> 8 bit lut for converting I->L images
    see https://github.com/python-pillow/Pillow/issues/440
    """
    im = hopper("I")
    im.point(list(range(256)) * 256, "L")


def test_f_lut():
    """Tests for floating point lut of 8bit gray image"""
    im = hopper("L")
    lut = [0.5 * float(x) for x in range(256)]

    out = im.point(lut, "F")

    int_lut = [x // 2 for x in range(256)]
    assert_image_equal(out.convert("L"), im.point(int_lut, "L"))


def test_f_mode():
    im = hopper("F")
    with pytest.raises(ValueError):
        im.point(None)
