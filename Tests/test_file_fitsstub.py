from io import BytesIO

import pytest

from PIL import FitsStubImagePlugin, Image

TEST_FILE = "Tests/images/hopper.fits"


def test_open():
    # Act
    with Image.open(TEST_FILE) as im:

        # Assert
        assert im.format == "FITS"
        assert im.size == (128, 128)
        assert im.mode == "L"


def test_invalid_file():
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        FitsStubImagePlugin.FITSStubImageFile(invalid_file)


def test_load():
    # Arrange
    with Image.open(TEST_FILE) as im:

        # Act / Assert: stub cannot load without an implemented handler
        with pytest.raises(OSError):
            im.load()


def test_truncated_fits():
    # No END to headers
    image_data = b"SIMPLE  =                    T" + b" " * 50 + b"TRUNCATE"
    with pytest.raises(OSError):
        FitsStubImagePlugin.FITSStubImageFile(BytesIO(image_data))


def test_naxis_zero():
    # This test image has been manually hexedited
    # to set the number of data axes to zero
    with pytest.raises(ValueError):
        with Image.open("Tests/images/hopper_naxis_zero.fits"):
            pass


def test_save():
    # Arrange
    with Image.open(TEST_FILE) as im:
        dummy_fp = None
        dummy_filename = "dummy.filename"

        # Act / Assert: stub cannot save without an implemented handler
        with pytest.raises(OSError):
            im.save(dummy_filename)
        with pytest.raises(OSError):
            FitsStubImagePlugin._save(im, dummy_fp, dummy_filename)
