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


@pytest.mark.parametrize(
    "rawmode, planes",
    (("P;2L", 2), ("P;4L", 4)),
)
@pytest.mark.parametrize("width", (8, 9, 16, 17))
def test_bit_planes_row_length(rawmode: str, planes: int, width: int) -> None:
    # Each bit plane is padded to a whole byte, so a row is
    # planes * ceil(width / 8) bytes rather than ceil(width * planes / 8)
    row = planes * ((width + 7) // 8)

    im = Image.frombytes("P", (width, 1), b"\x00" * row, "raw", rawmode, 0, 1)
    assert im.size == (width, 1)

    with pytest.raises(ValueError, match="not enough image data"):
        Image.frombytes("P", (width, 1), b"\x00" * (row - 1), "raw", rawmode, 0, 1)

    # a short final row must be rejected rather than read past the end of data
    with pytest.raises(ValueError, match="not enough image data"):
        Image.frombytes("P", (width, 2), b"\x00" * (2 * row - 1), "raw", rawmode, 0, 1)


def test_bit_planes_row_stride() -> None:
    # 4 bit planes of 2 bytes each per row, so the second row starts at offset 8
    data = bytes(
        (
            0x80, 0x00, 0x40, 0x00, 0x20, 0x00, 0x10, 0x80,
            0xFF, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        )
    )  # fmt: skip
    im = Image.frombytes("P", (9, 2), data, "raw", "P;4L", 0, 1)

    assert [im.getpixel((x, 0)) for x in range(9)] == [1, 2, 4, 8, 0, 0, 0, 0, 8]
    assert [im.getpixel((x, 1)) for x in range(9)] == [1, 1, 1, 1, 1, 1, 1, 1, 1]
