from __future__ import annotations

from typing import Any, NamedTuple

import pytest

from PIL import Image

from .helper import (
    assert_deep_equal,
    assert_image_equal,
    hopper,
    is_big_endian,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    import pyarrow
else:
    pyarrow = pytest.importorskip("pyarrow", reason="PyArrow not installed")

TEST_IMAGE_SIZE = (10, 10)


def _test_img_equals_pyarray(
    img: Image.Image, arr: Any, mask: list[int] | None, elts_per_pixel: int = 1
) -> None:
    assert img.height * img.width * elts_per_pixel == len(arr)
    px = img.load()
    assert px is not None
    if elts_per_pixel > 1 and mask is None:
        # have to do element wise comparison when we're comparing
        # flattened r,g,b,a to a pixel.
        mask = list(range(elts_per_pixel))
    for x in range(0, img.size[0], int(img.size[0] / 10)):
        for y in range(0, img.size[1], int(img.size[1] / 10)):
            if mask:
                pixel = px[x, y]
                assert isinstance(pixel, tuple)
                for ix, elt in enumerate(mask):
                    if elts_per_pixel == 1:
                        assert pixel[ix] == arr[y * img.width + x].as_py()[elt]
                    else:
                        assert (
                            pixel[ix]
                            == arr[(y * img.width + x) * elts_per_pixel + elt].as_py()
                        )
            else:
                assert_deep_equal(px[x, y], arr[y * img.width + x].as_py())


def _test_img_equals_int32_pyarray(
    img: Image.Image, arr: Any, mask: list[int] | None, elts_per_pixel: int = 1
) -> None:
    assert img.height * img.width * elts_per_pixel == len(arr)
    px = img.load()
    assert px is not None
    if mask is None:
        # have to do element wise comparison when we're comparing
        # flattened rgba in an uint32 to a pixel.
        mask = list(range(elts_per_pixel))
    for x in range(0, img.size[0], int(img.size[0] / 10)):
        for y in range(0, img.size[1], int(img.size[1] / 10)):
            pixel = px[x, y]
            assert isinstance(pixel, tuple)
            arr_pixel_int = arr[y * img.width + x].as_py()
            arr_pixel_tuple = (
                arr_pixel_int % 256,
                (arr_pixel_int // 256) % 256,
                (arr_pixel_int // 256**2) % 256,
                (arr_pixel_int // 256**3),
            )
            if is_big_endian():
                arr_pixel_tuple = arr_pixel_tuple[::-1]

            for ix, elt in enumerate(mask):
                assert pixel[ix] == arr_pixel_tuple[elt]


# really hard to get a non-nullable list type
fl_uint8_4_type = pyarrow.field(
    "_", pyarrow.list_(pyarrow.field("_", pyarrow.uint8()).with_nullable(False), 4)
).type


@pytest.mark.parametrize(
    "mode, dtype, mask",
    (
        ("L", pyarrow.uint8(), None),
        ("I", pyarrow.int32(), None),
        ("F", pyarrow.float32(), None),
        ("LA", fl_uint8_4_type, [0, 3]),
        ("RGB", fl_uint8_4_type, [0, 1, 2]),
        ("RGBA", fl_uint8_4_type, None),
        ("RGBX", fl_uint8_4_type, None),
        ("CMYK", fl_uint8_4_type, None),
        ("YCbCr", fl_uint8_4_type, [0, 1, 2]),
        ("HSV", fl_uint8_4_type, [0, 1, 2]),
    ),
)
def test_to_array(mode: str, dtype: pyarrow.DataType, mask: list[int] | None) -> None:
    img = hopper(mode)

    # Resize to non-square
    img = img.crop((3, 0, 124, 127))
    assert img.size == (121, 127)

    arr = pyarrow.array(img)  # type: ignore[call-overload]
    _test_img_equals_pyarray(img, arr, mask)
    assert arr.type == dtype

    reloaded = Image.fromarrow(arr, mode, img.size)

    assert reloaded

    assert_image_equal(img, reloaded)


def test_lifetime() -> None:
    # valgrind shouldn't error out here.
    # arrays should be accessible after the image is deleted.

    img = hopper("L")

    arr_1 = pyarrow.array(img)  # type: ignore[call-overload]
    arr_2 = pyarrow.array(img)  # type: ignore[call-overload]

    del img

    assert arr_1.sum().as_py() > 0
    del arr_1

    assert arr_2.sum().as_py() > 0
    del arr_2


def test_lifetime2() -> None:
    # valgrind shouldn't error out here.
    # img should remain after the arrays are collected.

    img = hopper("L")

    arr_1 = pyarrow.array(img)  # type: ignore[call-overload]
    arr_2 = pyarrow.array(img)  # type: ignore[call-overload]

    assert arr_1.sum().as_py() > 0
    del arr_1

    assert arr_2.sum().as_py() > 0
    del arr_2

    img2 = img.copy()
    px = img2.load()
    assert px  # make mypy happy
    assert isinstance(px[0, 0], int)


class DataShape(NamedTuple):
    dtype: pyarrow.DataType
    # Strictly speaking, elt should be a pixel or pixel component, so
    # list[uint8][4], float, int, uint32, uint8, etc.  But more
    # correctly, it should be exactly the dtype from the line above.
    elt: Any
    elts_per_pixel: int


UINT_ARR = DataShape(
    dtype=fl_uint8_4_type,
    elt=[1, 2, 3, 4],  # array of 4 uint8 per pixel
    elts_per_pixel=1,  # only one array per pixel
)

UINT = DataShape(
    dtype=pyarrow.uint8(),
    elt=3,  # one uint8,
    elts_per_pixel=4,  # but repeated 4x per pixel
)

UINT32 = DataShape(
    dtype=pyarrow.uint32(),
    elt=0xABCDEF45,  # one packed int, doesn't fit in a int32 > 0x80000000
    elts_per_pixel=1,  # one per pixel
)

INT32 = DataShape(
    dtype=pyarrow.uint32(),
    elt=0x12CDEF45,  # one packed int
    elts_per_pixel=1,  # one per pixel
)


@pytest.mark.parametrize(
    "mode, data_tp, mask",
    (
        ("L", DataShape(pyarrow.uint8(), 3, 1), None),
        ("I", DataShape(pyarrow.int32(), 1 << 24, 1), None),
        ("F", DataShape(pyarrow.float32(), 3.14159, 1), None),
        ("LA", UINT_ARR, [0, 3]),
        ("LA", UINT, [0, 3]),
        ("RGB", UINT_ARR, [0, 1, 2]),
        ("RGBA", UINT_ARR, None),
        ("CMYK", UINT_ARR, None),
        ("YCbCr", UINT_ARR, [0, 1, 2]),
        ("HSV", UINT_ARR, [0, 1, 2]),
        ("RGB", UINT, [0, 1, 2]),
        ("RGBA", UINT, None),
        ("CMYK", UINT, None),
        ("YCbCr", UINT, [0, 1, 2]),
        ("HSV", UINT, [0, 1, 2]),
    ),
)
def test_fromarray(mode: str, data_tp: DataShape, mask: list[int] | None) -> None:
    (dtype, elt, elts_per_pixel) = data_tp

    ct_pixels = TEST_IMAGE_SIZE[0] * TEST_IMAGE_SIZE[1]
    arr = pyarrow.array([elt] * (ct_pixels * elts_per_pixel), type=dtype)
    img = Image.fromarrow(arr, mode, TEST_IMAGE_SIZE)

    _test_img_equals_pyarray(img, arr, mask, elts_per_pixel)


@pytest.mark.parametrize(
    "mode, data_tp, mask",
    (
        ("LA", UINT32, [0, 3]),
        ("RGB", UINT32, [0, 1, 2]),
        ("RGBA", UINT32, None),
        ("CMYK", UINT32, None),
        ("YCbCr", UINT32, [0, 1, 2]),
        ("HSV", UINT32, [0, 1, 2]),
        ("LA", INT32, [0, 3]),
        ("RGB", INT32, [0, 1, 2]),
        ("RGBA", INT32, None),
        ("CMYK", INT32, None),
        ("YCbCr", INT32, [0, 1, 2]),
        ("HSV", INT32, [0, 1, 2]),
    ),
)
def test_from_int32array(mode: str, data_tp: DataShape, mask: list[int] | None) -> None:
    (dtype, elt, elts_per_pixel) = data_tp

    ct_pixels = TEST_IMAGE_SIZE[0] * TEST_IMAGE_SIZE[1]
    arr = pyarrow.array([elt] * (ct_pixels * elts_per_pixel), type=dtype)
    img = Image.fromarrow(arr, mode, TEST_IMAGE_SIZE)

    _test_img_equals_int32_pyarray(img, arr, mask, elts_per_pixel)
