from __future__ import annotations

import sys
from array import array

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper, is_big_endian


def test_getdata_sanity() -> None:
    data = hopper().getdata()

    len(data)
    list(data)

    assert data[0] == (20, 20, 70)


def test_putdata_sanity() -> None:
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


@pytest.mark.parametrize(
    "mode, first_pixel, data_size",
    (
        ("1", 0, 960),
        ("L", 17, 960),
        ("I", 17, 960),
        ("F", 17.0, 960),
        ("RGB", (11, 13, 52), 960),
        ("RGBA", (11, 13, 52, 255), 960),
        ("CMYK", (244, 242, 203, 0), 960),
        ("YCbCr", (16, 147, 123), 960),
    ),
)
def test_getdata_roundtrip(
    mode: str, first_pixel: float | tuple[int, ...], data_size: int
) -> None:
    im = hopper(mode).resize((32, 30), Image.Resampling.NEAREST)
    data = im.getdata()
    assert data[0] == first_pixel
    assert len(data) == data_size
    assert len(list(data)) == data_size


@pytest.mark.parametrize(
    "value, pixel",
    (
        (0xFFFFFFFF, (255, 255, 255, 255)),
        (-1, (255, 255, 255, 255)),
        (sys.maxsize, (255, 255, 255, 255 if sys.maxsize > 2**32 else 127)),
    ),
)
def test_putdata_long_integers(value: int, pixel: tuple[int, int, int, int]) -> None:
    # see bug-200802-systemerror

    im = Image.new("RGBA", (1, 1))
    im.putdata([value])
    assert im.getpixel((0, 0)) == pixel


def test_putdata_pypy_performance() -> None:
    im = Image.new("L", (256, 256))
    im.putdata(list(range(256)) * 256)


def test_putdata_mode_with_L_with_float() -> None:
    im = Image.new("L", (1, 1), 0)
    im.putdata([2.0])
    assert im.getpixel((0, 0)) == 2


@pytest.mark.parametrize("mode", ("I", "I;16", "I;16L", "I;16B"))
def test_putdata_mode_I(mode: str) -> None:
    src = hopper("L")
    data = list(src.getdata())
    im = Image.new(mode, src.size, 0)
    im.putdata(data, 2, 256)

    target = [2 * elt + 256 for elt in data]
    assert list(im.getdata()) == target


def test_putdata_mode_F() -> None:
    src = hopper("L")
    data = list(src.getdata())
    im = Image.new("F", src.size, 0)
    im.putdata(data, 2.0, 256.0)

    target = [2.0 * float(elt) + 256.0 for elt in data]
    assert list(im.getdata()) == target


@pytest.mark.parametrize("mode", ("BGR;15", "BGR;16", "BGR;24"))
def test_putdata_mode_BGR(mode: str) -> None:
    data = [(16, 32, 49), (32, 32, 98)]
    with pytest.warns(DeprecationWarning):
        im = Image.new(mode, (1, 2))
    im.putdata(data)

    assert list(im.getdata()) == data


def test_putdata_array_B() -> None:
    # shouldn't segfault
    # see https://github.com/python-pillow/Pillow/issues/1008

    arr = array("B", [0]) * 15000
    im = Image.new("L", (150, 100))
    im.putdata(arr)

    assert len(im.getdata()) == len(arr)


def test_putdata_array_F() -> None:
    # shouldn't segfault
    # see https://github.com/python-pillow/Pillow/issues/1008

    im = Image.new("F", (150, 100))
    arr = array("f", [0.0]) * 15000
    im.putdata(arr)

    assert len(im.getdata()) == len(arr)


def test_putdata_not_flattened() -> None:
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


@pytest.mark.parametrize("mode", Image.MODES + ["BGR;15", "BGR;16", "BGR;24"])
def test_getdata_putdata(mode: str) -> None:
    if is_big_endian() and mode == "BGR;15":
        pytest.xfail("Known failure of BGR;15 on big-endian")
    im = hopper(mode)
    if mode.startswith("BGR;"):
        with pytest.warns(DeprecationWarning):
            reloaded = Image.new(mode, im.size)
    else:
        reloaded = Image.new(mode, im.size)
    reloaded.putdata(im.getdata())
    assert_image_equal(im, reloaded)
