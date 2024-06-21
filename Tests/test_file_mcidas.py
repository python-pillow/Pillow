from __future__ import annotations

import pytest
from PIL import Image, McIdasImagePlugin
from .helper import assert_image_equal_tofile
from io import BytesIO
import struct

def create_mock_mcidas_file(w11_value: int) -> BytesIO:
    """
    Creates a mock McIdas file with a given w[11] value.
    """
    header = struct.pack(
        "!64i",
        0, 0, 0, 0, 0, 0, 0, 4,  # Prefix (first 8 bytes)
        0, 400, 1800,  # Width, Height (w[9], w[10])
        w11_value,  # Mode (w[11])
        0, 0, 0,  # w[12] to w[14]
        16,  # w[15] (assuming some stride value)
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # w[16] to w[25]
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # w[26] to w[35]
        256,  # w[34] (assuming some offset)
    )
    # Ensure header length is 256 bytes
    header = b"\x00" * (256 - len(header)) + header

    # Create a valid file
    return BytesIO(header)

def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"
    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(invalid_file)

def test_valid_file() -> None:
    # Arrange
    test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"
    saved_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.tiff"

    # Act
    with Image.open(test_file) as im:
        im.load()
        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (1800, 400)
        assert_image_equal_tofile(im, saved_file)

def test_8bit_file() -> None:
    # Arrange
    test_file = create_mock_mcidas_file(1)

    # Act
    with Image.open(test_file) as im:
        im.load()
        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "L"
        assert im.size == (1800, 400)

def test_32bit_file() -> None:
    # Arrange
    test_file = create_mock_mcidas_file(4)

    # Act
    with Image.open(test_file) as im:
        im.load()
        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (1800, 400)

def test_unsupported_file() -> None:
    # Arrange
    test_file = create_mock_mcidas_file(3)

    # Act & Assert
    with pytest.raises(SyntaxError, match="unsupported McIdas format"):
        Image.open(test_file)
