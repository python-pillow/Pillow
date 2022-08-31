import pytest

from PIL.Image import Transpose

from . import helper
from .helper import assert_image_equal

HOPPER = {
    mode: helper.hopper(mode).crop((0, 0, 121, 127)).copy()
    for mode in ["L", "RGB", "I;16", "I;16L", "I;16B"]
}


@pytest.mark.parametrize("mode", HOPPER)
def test_flip_left_right(mode):
    im = HOPPER[mode]
    out = im.transpose(Transpose.FLIP_LEFT_RIGHT)
    assert out.mode == mode
    assert out.size == im.size

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((x - 2, 1))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, 1))
    assert im.getpixel((1, y - 2)) == out.getpixel((x - 2, y - 2))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, y - 2))


@pytest.mark.parametrize("mode", HOPPER)
def test_flip_top_bottom(mode):
    im = HOPPER[mode]
    out = im.transpose(Transpose.FLIP_TOP_BOTTOM)
    assert out.mode == mode
    assert out.size == im.size

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((1, y - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((x - 2, y - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((1, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((x - 2, 1))


@pytest.mark.parametrize("mode", HOPPER)
def test_rotate_90(mode):
    im = HOPPER[mode]
    out = im.transpose(Transpose.ROTATE_90)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((1, x - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, 1))
    assert im.getpixel((1, y - 2)) == out.getpixel((y - 2, x - 2))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((y - 2, 1))


@pytest.mark.parametrize("mode", HOPPER)
def test_rotate_180(mode):
    im = HOPPER[mode]
    out = im.transpose(Transpose.ROTATE_180)
    assert out.mode == mode
    assert out.size == im.size

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((x - 2, y - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, y - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((x - 2, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, 1))


@pytest.mark.parametrize("mode", HOPPER)
def test_rotate_270(mode):
    im = HOPPER[mode]
    out = im.transpose(Transpose.ROTATE_270)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((y - 2, 1))
    assert im.getpixel((x - 2, 1)) == out.getpixel((y - 2, x - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((1, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, x - 2))


@pytest.mark.parametrize("mode", HOPPER)
def test_transpose(mode):
    im = HOPPER[mode]
    out = im.transpose(Transpose.TRANSPOSE)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((1, 1))
    assert im.getpixel((x - 2, 1)) == out.getpixel((1, x - 2))
    assert im.getpixel((1, y - 2)) == out.getpixel((y - 2, 1))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((y - 2, x - 2))


@pytest.mark.parametrize("mode", HOPPER)
def test_tranverse(mode):
    im = HOPPER[mode]
    out = im.transpose(Transpose.TRANSVERSE)
    assert out.mode == mode
    assert out.size == im.size[::-1]

    x, y = im.size
    assert im.getpixel((1, 1)) == out.getpixel((y - 2, x - 2))
    assert im.getpixel((x - 2, 1)) == out.getpixel((y - 2, 1))
    assert im.getpixel((1, y - 2)) == out.getpixel((1, x - 2))
    assert im.getpixel((x - 2, y - 2)) == out.getpixel((1, 1))


@pytest.mark.parametrize("mode", HOPPER)
def test_roundtrip(mode):
    im = HOPPER[mode]

    def transpose(first, second):
        return im.transpose(first).transpose(second)

    assert_image_equal(
        im, transpose(Transpose.FLIP_LEFT_RIGHT, Transpose.FLIP_LEFT_RIGHT)
    )
    assert_image_equal(
        im, transpose(Transpose.FLIP_TOP_BOTTOM, Transpose.FLIP_TOP_BOTTOM)
    )
    assert_image_equal(im, transpose(Transpose.ROTATE_90, Transpose.ROTATE_270))
    assert_image_equal(im, transpose(Transpose.ROTATE_180, Transpose.ROTATE_180))
    assert_image_equal(
        im.transpose(Transpose.TRANSPOSE),
        transpose(Transpose.ROTATE_90, Transpose.FLIP_TOP_BOTTOM),
    )
    assert_image_equal(
        im.transpose(Transpose.TRANSPOSE),
        transpose(Transpose.ROTATE_270, Transpose.FLIP_LEFT_RIGHT),
    )
    assert_image_equal(
        im.transpose(Transpose.TRANSVERSE),
        transpose(Transpose.ROTATE_90, Transpose.FLIP_LEFT_RIGHT),
    )
    assert_image_equal(
        im.transpose(Transpose.TRANSVERSE),
        transpose(Transpose.ROTATE_270, Transpose.FLIP_TOP_BOTTOM),
    )
    assert_image_equal(
        im.transpose(Transpose.TRANSVERSE),
        transpose(Transpose.ROTATE_180, Transpose.TRANSPOSE),
    )
