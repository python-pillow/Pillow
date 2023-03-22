import pytest

from PIL import GribStubImagePlugin, Image

from .helper import hopper

TEST_FILE = "Tests/images/WAlaska.wind.7days.grb"


def test_open():
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.format == "GRIB"

        # Dummy data from the stub
        assert im.mode == "F"
        assert im.size == (1, 1)


def test_invalid_file():
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        GribStubImagePlugin.GribStubImageFile(invalid_file)


def test_load():
    # Arrange
    with Image.open(TEST_FILE) as im:
        # Act / Assert: stub cannot load without an implemented handler
        with pytest.raises(OSError):
            im.load()


def test_save(tmp_path):
    # Arrange
    im = hopper()
    tmpfile = str(tmp_path / "temp.grib")

    # Act / Assert: stub cannot save without an implemented handler
    with pytest.raises(OSError):
        im.save(tmpfile)


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
    GribStubImagePlugin.register_handler(handler)
    with Image.open(TEST_FILE) as im:
        assert handler.opened
        assert not handler.loaded

        im.load()
        assert handler.loaded

        temp_file = str(tmp_path / "temp.grib")
        im.save(temp_file)
        assert handler.saved

    GribStubImagePlugin._handler = None
