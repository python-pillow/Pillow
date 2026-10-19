from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image, ImageFile

from .helper import assert_image_equal, hopper


@pytest.mark.parametrize("data_type", ("bytes", "memoryview"))
def test_sanity(data_type: str) -> None:
    im1 = hopper()

    data: bytes | memoryview = im1.tobytes()
    if data_type == "memoryview":
        data = memoryview(data)
    im2 = Image.frombytes(im1.mode, im1.size, data)

    assert_image_equal(im1, im2)


def test_readonly_buffer() -> None:
    data = bytes(4)
    im = Image.frombuffer("L", (2, 2), data, "raw", "L", 0, 1)
    assert im.readonly

    im.frombytes(b"\x01" * 4)
    assert not im.readonly
    assert im.getpixel((0, 0)) == 1
    assert data == bytes(4)


def test_readonly_file() -> None:
    with Image.open("Tests/images/hopper_8bit.pgm") as im:
        im.load()
        assert im.readonly

        im.frombytes(b"\x01" * im.width * im.height)
        assert not im.readonly
        assert im.getpixel((0, 0)) == 1


def test_from_load() -> None:
    class LoadImageFile(ImageFile.ImageFile):
        loaded = False

        def _open(self) -> None:
            self._mode = "L"
            self._size = (1, 1)

        def load(self) -> Image.core.PixelAccess | None:
            if not self.loaded:
                self.im = self.core = Image.core.new(self.mode, self.size)
                self.frombytes(b"\x01")
                self.loaded = True
            return super().load()

    with LoadImageFile(BytesIO()) as im:
        assert im.getpixel((0, 0)) == 1
        assert im.im is im.core
