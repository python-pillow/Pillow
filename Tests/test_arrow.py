from __future__ import annotations

from typing import Any  # undone

import pytest

from PIL import Image

from .helper import (
    assert_deep_equal,
    assert_image_equal,
    hopper,
)

pyarrow = pytest.importorskip("pyarrow", reason="PyArrow not installed")

TEST_IMAGE_SIZE = (10, 10)


def _test_img_equals_pyarray(img: Image.Image, arr: Any, mask) -> None:
    assert img.height * img.width == len(arr)
    px = img.load()
    assert px is not None
    for x in range(0, img.size[0], int(img.size[0] / 10)):
        for y in range(0, img.size[1], int(img.size[1] / 10)):
            if mask:
                for ix, elt in enumerate(mask):
                    assert px[x, y][ix] == arr[y * img.width + x].as_py()[elt]
            else:
                assert_deep_equal(px[x, y], arr[y * img.width + x].as_py())


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
def test_to_array(mode: str, dtype: Any, mask: Any) -> None:
    img = hopper(mode)

    # Resize to non-square
    img = img.crop((3, 0, 124, 127))
    assert img.size == (121, 127)

    arr = pyarrow.array(img)
    _test_img_equals_pyarray(img, arr, mask)
    assert arr.type == dtype

    reloaded = Image.fromarrow(arr, mode, img.size)

    assert reloaded

    assert_image_equal(img, reloaded)


@pytest.mark.parametrize(
    "mode, dest_modes",
    (
        ("L", ["I", "F", "LA", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr", "HSV"]),
        ("I", ["L", "F"]),  # Technically I32 can work for any 4x8bit storage.
        ("F", ["I", "L", "LA", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr", "HSV"]),
        ("LA", ["L", "F"]),
        ("RGB", ["L", "F"]),
        ("RGBA", ["L", "F"]),
        ("RGBX", ["L", "F"]),
        ("CMYK", ["L", "F"]),
        ("YCbCr", ["L", "F"]),
        ("HSV", ["L", "F"]),
    ),
)
def test_invalid_array_type(mode: str, dest_modes: List[str]) -> None:
    img = hopper(mode)
    for dest_mode in dest_modes:
        with pytest.raises(ValueError):
            Image.fromarrow(img, dest_mode, img.size)


def test_invalid_array_size():
    img = hopper("RGB")

    assert img.size != (10, 10)
    with pytest.raises(ValueError):
        Image.fromarrow(img, "RGB", (10, 10))


def test_lifetime():
    # valgrind shouldn't error out here.
    # arrays should be accessible after the image is deleted.

    img = hopper("L")

    arr_1 = pyarrow.array(img)
    arr_2 = pyarrow.array(img)

    del img

    assert arr_1.sum().as_py() > 0
    del arr_1

    assert arr_2.sum().as_py() > 0
    del arr_2


def test_lifetime2():
    # valgrind shouldn't error out here.
    # img should remain after the arrays are collected.

    img = hopper("L")

    arr_1 = pyarrow.array(img)
    arr_2 = pyarrow.array(img)

    assert arr_1.sum().as_py() > 0
    del arr_1

    assert arr_2.sum().as_py() > 0
    del arr_2

    img2 = img.copy()
    px = img2.load()
    assert isinstance(px[0, 0], int)


def test_release_schema():
    # these should not error out, valgrind should be clean
    img = hopper("L")
    schema = img.__arrow_c_schema__()
    del schema


def test_release_array():
    # these should not error out, valgrind should be clean
    img = hopper("L")
    array, schema = img.__arrow_c_array__()
    del array
    del schema


def test_readonly():
    img = hopper("L")
    reloaded = Image.fromarrow(img, img.mode, img.size)
    assert reloaded.readonly == 1
    reloaded._readonly = 0
    assert reloaded.readonly == 1


def test_multiblock_l_image():
    block_size = Image.core.get_block_size()

    # check a 2 block image in single channel mode
    size = (4096, 2 * block_size // 4096)
    img = Image.new("L", size, 128)

    with pytest.raises(ValueError):
        (schema, arr) = img.__arrow_c_array__()


def test_multiblock__rgba_image():
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))

    with pytest.raises(ValueError):
        (schema, arr) = img.__arrow_c_array__()


def test_multiblock_l_schema():
    block_size = Image.core.get_block_size()

    # check a 2 block image in single channel mode
    size = (4096, 2 * block_size // 4096)
    img = Image.new("L", size, 128)

    with pytest.raises(ValueError):
        schema = img.__arrow_c_schema__()


def test_multiblock__rgba_schema():
    block_size = Image.core.get_block_size()

    # check a 2 block image in 4 channel mode
    size = (4096, (block_size // 4096) // 2)
    img = Image.new("RGBA", size, (128, 127, 126, 125))

    with pytest.raises(ValueError):
        schema = img.__arrow_c_schema__()
