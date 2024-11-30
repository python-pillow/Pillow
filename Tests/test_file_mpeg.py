from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image, MpegImagePlugin


def test_identify() -> None:
    # Arrange
    b = BytesIO(b"\x00\x00\x01\xb3\x01\x00\x01")

    # Act
    with Image.open(b) as im:
        # Assert
        assert im.format == "MPEG"

        assert im.mode == "RGB"
        assert im.size == (16, 1)


def test_invalid_file() -> None:
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        MpegImagePlugin.MpegImageFile(invalid_file)


def test_load() -> None:
    # Arrange
    b = BytesIO(b"\x00\x00\x01\xb3\x01\x00\x01")

    with Image.open(b) as im:
        # Act / Assert: cannot load
        with pytest.raises(OSError):
            im.load()
