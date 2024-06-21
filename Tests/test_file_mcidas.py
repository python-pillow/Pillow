from __future__ import annotations

import struct
import pytest

from PIL import Image, McIdasImagePlugin

from .helper import assert_image_equal_tofile


def create_mock_file(filename: str, w11_value: int, width: int, height: int) -> None:
    """
    Create a mock McIdas area file with specified w[11] value, width, and height.
    """
    area_descriptor = [0] * 64
    area_descriptor[10] = width
    area_descriptor[9] = height
    area_descriptor[11] = w11_value
    area_descriptor[34] = 256  # arbitrary valid offset
    area_descriptor[15] = 0  # stride (arbitrary valid value)
    header = b"\x00" * 8 + struct.pack("!64i", *area_descriptor)

    with open(filename, "wb") as f:
        f.write(header)
        # Write image data (size based on width, height, and mode)
        if w11_value == 1:
            f.write(b"\x00" * (width * height))  # 8-bit data for mode L
        elif w11_value == 2:
            f.write(b"\x00" * (2 * width * height))  # 16-bit data for mode I;16B
        elif w11_value == 4:
            f.write(b"\x00" * (4 * width * height))  # 32-bit data for mode I;32B


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(invalid_file)


def test_valid_file() -> None:
    # Arrange
    # https://ghrc.nsstc.nasa.gov/hydro/details/cmx3g8
    # https://ghrc.nsstc.nasa.gov/pub/fieldCampaigns/camex3/cmx3g8/browse/
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


def test_mode_L() -> None:
    test_file = "Tests/images/mcidas_mode_L.ara"

    # Create mock file for mode L
    create_mock_file(test_file, w11_value=1, width=100, height=100)

    with Image.open(test_file) as im:
        im.load()
        assert im.format == "MCIDAS"
        assert im.mode == "L"
        assert im.size == (100, 100)


def test_mode_I_32B() -> None:
    test_file = "Tests/images/mcidas_mode_I_32B.ara"

    # Create mock file for mode I;32B
    create_mock_file(test_file, w11_value=4, width=100, height=100)

    with Image.open(test_file) as im:
        im.load()
        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (100, 100)


def test_unsupported_format() -> None:
    test_file = "Tests/images/mcidas_unsupported.ara"

    # Create mock file for unsupported format
    create_mock_file(test_file, w11_value=3, width=100, height=100)

    with pytest.raises(SyntaxError, match="unsupported McIdas format"):
        McIdasImagePlugin.McIdasImageFile(test_file)
