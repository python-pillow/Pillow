from __future__ import annotations

from io import BytesIO

import pytest

from PIL import GdImageFile, Image, UnidentifiedImageError, _binary

from .helper import assert_image_similar_tofile

TEST_GD_FILE = "Tests/images/hopper.gd"


def test_sanity() -> None:
    with GdImageFile.open(TEST_GD_FILE) as im:
        assert im.size == (128, 128)
        assert im.format == "GD"
        assert_image_similar_tofile(im.convert("RGB"), "Tests/images/hopper.jpg", 14)


def test_transparency() -> None:
    with open(TEST_GD_FILE, "rb") as fp:
        data = bytearray(fp.read())
    data[7:11] = b"\x00\x00\x00\x05"
    with GdImageFile.open(BytesIO(data)) as im:
        assert im.info["transparency"] == 5


def test_bad_mode() -> None:
    with pytest.raises(ValueError):
        GdImageFile.open(TEST_GD_FILE, "bad mode")


def test_decompression_bomb() -> None:
    b = BytesIO(_binary.o16be(65535) + _binary.o16be(50000) + _binary.o16be(50000))
    with pytest.raises(Image.DecompressionBombError):
        GdImageFile.open(b)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(UnidentifiedImageError):
        GdImageFile.open(invalid_file)
