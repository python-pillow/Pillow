from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper


@pytest.mark.parametrize("data_type", ("bytes", "memoryview"))
def test_sanity(data_type: str) -> None:
    im1 = hopper()

    data: bytes | memoryview = im1.tobytes()
    if data_type == "memoryview":
        data = memoryview(data)
    im2 = Image.frombytes(im1.mode, im1.size, data)

    assert_image_equal(im1, im2)
