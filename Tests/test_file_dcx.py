from __future__ import annotations

import warnings
from io import BytesIO

import pytest

from PIL import DcxImagePlugin, Image
from PIL._binary import o16le as o16
from PIL._binary import o32le as o32

from .helper import assert_image_equal, hopper, is_pypy

# Created with ImageMagick: convert hopper.ppm hopper.dcx
TEST_FILE = "Tests/images/hopper.dcx"


def test_sanity() -> None:
    # Arrange

    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.size == (128, 128)
        assert isinstance(im, DcxImagePlugin.DcxImageFile)
        orig = hopper()
        assert_image_equal(im, orig)


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open_test_image() -> None:
        im = Image.open(TEST_FILE)
        im.load()

    with pytest.warns(ResourceWarning):
        open_test_image()


def test_closed_file() -> None:
    with warnings.catch_warnings(action="error"):
        im = Image.open(TEST_FILE)
        im.load()
        im.close()


def test_context_manager() -> None:
    with warnings.catch_warnings(action="error"):
        with Image.open(TEST_FILE) as im:
            im.load()


def test_invalid_file() -> None:
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            DcxImagePlugin.DcxImageFile(fp)


def test_tell() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        # Act
        frame = im.tell()

        # Assert
        assert frame == 0


def test_n_frames() -> None:
    with Image.open(TEST_FILE) as im:
        assert isinstance(im, DcxImagePlugin.DcxImageFile)
        assert im.n_frames == 1
        assert not im.is_animated


def test_eoferror() -> None:
    with Image.open(TEST_FILE) as im:
        assert isinstance(im, DcxImagePlugin.DcxImageFile)
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_seek_too_far() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        frame = 999  # too big on purpose

    # Act / Assert
    with pytest.raises(EOFError):
        im.seek(frame)


def test_seek_frame_with_different_mode() -> None:
    # A later frame may use a different mode and pixel size than the first.
    # The backing image must not be reused across such a change.
    def pcx(bits: int, planes: int, w: int, h: int, body: bytes) -> bytes:
        stride = (w * bits + 7) // 8
        stride += stride % 2
        header = bytes([10, 5, 1, bits])
        header += o16(0) + o16(0) + o16(w - 1) + o16(h - 1) + o16(72) + o16(72)
        header += bytes(48) + b"\0" + bytes([planes]) + o16(stride)
        return header + bytes(128 - len(header)) + body

    w = h = 128
    first_frame = pcx(8, 1, w, h, b"\x41" * (w * h))
    second_frame = pcx(8, 3, w, h, b"\x41" * (3 * w * h))
    b = BytesIO(
        o32(DcxImagePlugin.MAGIC)
        + o32(16)
        + o32(len(first_frame) + 16)
        + o32(0)
        + first_frame
        + second_frame
    )
    with Image.open(b) as im:
        im.load()
        assert im.mode == "L"
        im.seek(1)
        im.load()
        assert im.mode == "RGB"
        assert im.getpixel((0, 0)) == (0x41, 0x41, 0x41)


def test_seek_decompression_bomb() -> None:
    with open("Tests/images/pil184.pcx", "rb") as fp:
        first_frame = fp.read()
    second_frame = first_frame[:8] + o16(65535) + o16(65535) + first_frame[12:]
    b = BytesIO(
        o32(DcxImagePlugin.MAGIC)
        + o32(16)
        + o32(len(first_frame) + 16)
        + o32(0)
        + first_frame
        + second_frame
    )
    with Image.open(b) as im:
        with pytest.raises(Image.DecompressionBombError):
            im.seek(1)
