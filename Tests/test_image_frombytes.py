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


@pytest.mark.parametrize("mode", ("L", "RGBA"))
def test_readonly_buffer(mode: str) -> None:
    size = (2, 2)
    length = 4 * Image.getmodebands(mode)
    data = bytes(bytearray(length))
    im = Image.frombuffer(mode, size, data, "raw", mode, 0, 1)
    assert im.readonly

    replacement = b"\x01" * length
    im.frombytes(replacement)

    assert im.tobytes() == replacement
    assert data == bytes(length)
    assert not im.readonly


def test_mutable_core_with_readonly_image() -> None:
    # Plugins may call frombytes() from load() before clearing the image's flag.
    im = Image.new("L", (2, 2))
    im.readonly = 1
    core = im.im

    im.frombytes(b"\x01" * 4)

    assert im.im is core
    assert im.tobytes() == b"\x01" * 4
