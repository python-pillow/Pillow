from __future__ import annotations

import sys
from array import array

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper


def test_sanity() -> None:
    im1 = hopper()

    data = list(im1.getdata())

    im2 = Image.new(im1.mode, im1.size, 0)
    im2.putdata(data)

    assert_image_equal(im1, im2)

    # readonly
    im2 = Image.new(im1.mode, im2.size, 0)
    im2.readonly = 1
    im2.putdata(data)

    assert not im2.readonly
    assert_image_equal(im1, im2)


def test_long_integers() -> None:
    # see bug-200802-systemerror
    def put(value: int) -> float | tuple[int, ...] | None:
        im = Image.new("RGBA", (1, 1))
        im.putdata([value])
        return im.getpixel((0, 0))

    assert put(0xFFFFFFFF) == (255, 255, 255, 255)
    assert put(0xFFFFFFFF) == (255, 255, 255, 255)
    assert put(-1) == (255, 255, 255, 255)
    assert put(-1) == (255, 255, 255, 255)
    if sys.maxsize > 2**32:
        assert put(sys.maxsize) == (255, 255, 255, 255)
    else:
        assert put(sys.maxsize) == (255, 255, 255, 127)


def test_pypy_performance() -> None:
    im = Image.new("L", (256, 256))
    im.putdata(list(range(256)) * 256)


def test_mode_with_L_with_float() -> None:
    im = Image.new("L", (1, 1), 0)
    im.putdata([2.0])
    assert im.getpixel((0, 0)) == 2


@pytest.mark.parametrize("mode", ("I", "I;16", "I;16L", "I;16B"))
def test_mode_i(mode: str) -> None:
    src = hopper("L")
    data = list(src.getdata())
    im = Image.new(mode, src.size, 0)
    im.putdata(data, 2, 256)

    target = [2 * elt + 256 for elt in data]
    assert list(im.getdata()) == target


def test_mode_F() -> None:
    src = hopper("L")
    data = list(src.getdata())
    im = Image.new("F", src.size, 0)
    im.putdata(data, 2.0, 256.0)

    target = [2.0 * float(elt) + 256.0 for elt in data]
    assert list(im.getdata()) == target


@pytest.mark.parametrize("mode", ("BGR;15", "BGR;16", "BGR;24"))
def test_mode_BGR(mode: str) -> None:
    data = [(16, 32, 49), (32, 32, 98)]
    with pytest.warns(DeprecationWarning, match=mode):
        im = Image.new(mode, (1, 2))
    im.putdata(data)

    assert list(im.getdata()) == data


def test_array_B() -> None:
    # shouldn't segfault
    # see https://github.com/python-pillow/Pillow/issues/1008

    arr = array("B", [0]) * 15000
    im = Image.new("L", (150, 100))
    im.putdata(arr)

    assert len(im.getdata()) == len(arr)


def test_array_F() -> None:
    # shouldn't segfault
    # see https://github.com/python-pillow/Pillow/issues/1008

    im = Image.new("F", (150, 100))
    arr = array("f", [0.0]) * 15000
    im.putdata(arr)

    assert len(im.getdata()) == len(arr)


def test_not_flattened() -> None:
    im = Image.new("L", (1, 1))
    with pytest.raises(TypeError):
        im.putdata([[0]])
    with pytest.raises(TypeError):
        im.putdata([[0]], 2)

    with pytest.raises(TypeError):
        im = Image.new("I", (1, 1))
        im.putdata([[0]])
    with pytest.raises(TypeError):
        im = Image.new("F", (1, 1))
        im.putdata([[0]])
