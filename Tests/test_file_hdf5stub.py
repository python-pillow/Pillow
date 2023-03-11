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


def test_handler(tmp_path):
    class TestHandler:
        opened = False
        loaded = False
        saved = False

        def open(self, im):
            self.opened = True

        def load(self, im):
            self.loaded = True
            im.fp.close()
            return Image.new("RGB", (1, 1))

        def save(self, im, fp, filename):
            self.saved = True

    handler = TestHandler()
    Hdf5StubImagePlugin.register_handler(handler)
    with Image.open(TEST_FILE) as im:
        assert handler.opened
        assert not handler.loaded

        im.load()
        assert handler.loaded

        temp_file = str(tmp_path / "temp.h5")
        im.save(temp_file)
        assert handler.saved

    Hdf5StubImagePlugin._handler = None
