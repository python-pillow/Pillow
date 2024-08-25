from __future__ import annotations

import warnings

import pytest

from PIL import Image

from .helper import assert_deep_equal, assert_image, hopper, skip_unless_feature

from typing import Any # undone

pyarrow = pytest.importorskip("pyarrow", reason="PyArrow not installed")

TEST_IMAGE_SIZE = (10, 10)
from numbers import Number


def _test_img_equals_pyarray(img: Image.Image, arr: Any, mask) -> None:
    assert img.height * img.width == len(arr)
    px = img.load()
    assert px is not None
    for x in range(0, img.size[0], int(img.size[0] / 10)):
        for y in range(0, img.size[1], int(img.size[1] / 10)):
            if mask:
                for ix, elt in enumerate(mask):
                    assert px[x,y][ix] == arr[y * img.width + x].as_py()[elt]
            else:
                assert_deep_equal(px[x, y], arr[y * img.width + x].as_py())


# really hard to get a non-nullable list type
fl_uint8_4_type = pyarrow.field("_",
                           pyarrow.list_(
                               pyarrow.field("_",
                                        pyarrow.uint8()
                                        ).with_nullable(False)
                               ,4)
                           ).type

@pytest.mark.parametrize(
    "mode, dtype, mask",
    (
        ("L", pyarrow.uint8(), None),
        ("I", pyarrow.int32(), None),
        ("F", pyarrow.float32(), None),
        ("LA", fl_uint8_4_type, [0,3]),
        ("RGB", fl_uint8_4_type, [0,1,2]),
        ("RGBA", fl_uint8_4_type, None),
        ("RGBX", fl_uint8_4_type, None),
        ("CMYK", fl_uint8_4_type, None),
        ("YCbCr", fl_uint8_4_type, [0,1,2]),
        ("HSV", fl_uint8_4_type, [0,1,2]),
    ),
)
def test_to_array(mode: str, dtype: Any, mask: Any ) -> None:
    img = hopper(mode)

    # Resize to non-square
    img = img.crop((3, 0, 124, 127))
    assert img.size == (121, 127)

    arr = pyarrow.array(img)
    _test_img_equals_pyarray(img, arr, mask)
    assert arr.type == dtype
