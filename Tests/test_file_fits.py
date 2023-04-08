from io import BytesIO

import pytest

from PIL import FitsImagePlugin, Image

from .helper import assert_image_equal, hopper

TEST_FILE = "Tests/images/hopper.fits"


def test_open():
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.format == "FITS"
        assert im.size == (128, 128)
        assert im.mode == "L"

        assert_image_equal(im, hopper("L"))


def test_invalid_file():
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        FitsImagePlugin.FitsImageFile(invalid_file)


def test_truncated_fits():
    # No END to headers
    image_data = b"SIMPLE  =                    T" + b" " * 50 + b"TRUNCATE"
    with pytest.raises(OSError):
        FitsImagePlugin.FitsImageFile(BytesIO(image_data))


def test_naxis_zero():
    # This test image has been manually hexedited
    # to set the number of data axes to zero
    with pytest.raises(ValueError):
        with Image.open("Tests/images/hopper_naxis_zero.fits"):
            pass


def test_comment():
    image_data = b"SIMPLE  =                    T / comment string"
    with pytest.raises(OSError):
        FitsImagePlugin.FitsImageFile(BytesIO(image_data))
