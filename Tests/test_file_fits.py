from __future__ import annotations

from io import BytesIO

import pytest

from PIL import FitsImagePlugin, Image

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

TEST_FILE = "Tests/images/hopper.fits"


def test_open() -> None:
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.format == "FITS"
        assert im.size == (128, 128)
        assert im.mode == "L"

        assert_image_equal(im, hopper("L"))


def test_gzip1() -> None:
    with Image.open("Tests/images/m13_gzip.fits") as im:
        assert_image_equal_tofile(im, "Tests/images/m13.fits")


def test_invalid_file() -> None:
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        FitsImagePlugin.FitsImageFile(invalid_file)


def test_truncated_fits() -> None:
    # No END to headers
    image_data = b"SIMPLE  =                    T" + b" " * 50 + b"TRUNCATE"
    with pytest.raises(OSError):
        FitsImagePlugin.FitsImageFile(BytesIO(image_data))


def test_naxis_zero() -> None:
    image_data = b"".join(
        data.ljust(80, b" ") for data in [b"SIMPLE  = T", b"NAXIS   = 0", b"END"]
    ).ljust(2881)
    with pytest.raises(ValueError, match="No image data"):
        with Image.open(BytesIO(image_data)):
            pass


def test_comment() -> None:
    image_data = b"SIMPLE  =                    T / comment string"
    with pytest.raises(OSError):
        FitsImagePlugin.FitsImageFile(BytesIO(image_data))
