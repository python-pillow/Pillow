import pytest

from PIL import Hdf5StubImagePlugin, Image

TEST_FILE = "Tests/images/hdf5.h5"


def test_open():
    # Act
    with Image.open(TEST_FILE) as im:

        # Assert
        assert im.format == "HDF5"

        # Dummy data from the stub
        assert im.mode == "F"
        assert im.size == (1, 1)


def test_invalid_file():
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        Hdf5StubImagePlugin.HDF5StubImageFile(invalid_file)


def test_load():
    # Arrange
    with Image.open(TEST_FILE) as im:

        # Act / Assert: stub cannot load without an implemented handler
        with pytest.raises(OSError):
            im.load()


def test_save():
    # Arrange
    with Image.open(TEST_FILE) as im:
        dummy_fp = None
        dummy_filename = "dummy.filename"

        # Act / Assert: stub cannot save without an implemented handler
        with pytest.raises(OSError):
            im.save(dummy_filename)
        with pytest.raises(OSError):
            Hdf5StubImagePlugin._save(im, dummy_fp, dummy_filename)
