from __future__ import annotations

from io import BytesIO

import pytest

from PIL import CurImagePlugin, Image
from PIL._binary import o8
from PIL._binary import o16le as o16
from PIL._binary import o32le as o32

TEST_FILE = "Tests/images/deerstalker.cur"


def test_sanity() -> None:
    with Image.open(TEST_FILE) as im:
        assert im.size == (32, 32)
        assert isinstance(im, CurImagePlugin.CurImageFile)
        # Check some pixel colors to ensure image is loaded properly
        assert im.getpixel((10, 1)) == (0, 0, 0, 0)
        assert im.getpixel((11, 1)) == (253, 254, 254, 1)
        assert im.getpixel((16, 16)) == (84, 87, 86, 255)


def test_largest_cursor() -> None:
    magic = b"\x00\x00\x02\x00"
    sizes = ((1, 1), (8, 8), (4, 4))
    data = magic + o16(len(sizes))
    for w, h in sizes:
        image_offset = 6 + len(sizes) * 16 if (w, h) == max(sizes) else 0
        data += o8(w) + o8(h) + o8(0) * 10 + o32(image_offset)
    data += (
        o32(12)  # header size
        + o16(8)  # width
        + o16(16)  # height
        + o16(0)  # planes
        + o16(1)  # bits
    )
    with Image.open(BytesIO(data)) as im:
        assert im.size == (8, 8)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        CurImagePlugin.CurImageFile(invalid_file)

    no_cursors_file = "Tests/images/no_cursors.cur"

    cur = CurImagePlugin.CurImageFile(TEST_FILE)
    assert cur.fp is not None
    cur.fp.close()
    with open(no_cursors_file, "rb") as cur.fp:
        with pytest.raises(TypeError):
            cur._open()
