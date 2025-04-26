from __future__ import annotations

from pathlib import Path
from typing import IO

import pytest

from PIL import GribStubImagePlugin, Image, ImageFile

from .helper import hopper

TEST_FILE = "Tests/images/WAlaska.wind.7days.grb"


def test_open() -> None:
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.format == "GRIB"

        # Dummy data from the stub
        assert im.mode == "F"
        assert im.size == (1, 1)


def test_invalid_file() -> None:
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        GribStubImagePlugin.GribStubImageFile(invalid_file)


def test_load() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        # Act / Assert: stub cannot load without an implemented handler
        with pytest.raises(OSError):
            im.load()


def test_save(tmp_path: Path) -> None:
    # Arrange
    im = hopper()
    tmpfile = tmp_path / "temp.grib"

    # Act / Assert: stub cannot save without an implemented handler
    with pytest.raises(OSError):
        im.save(tmpfile)


def test_handler(tmp_path: Path) -> None:
    class TestHandler(ImageFile.StubHandler):
        opened = False
        loaded = False
        saved = False

        def open(self, im: Image.Image) -> None:
            self.opened = True

        def load(self, im: Image.Image) -> Image.Image:
            self.loaded = True
            im.fp.close()
            return Image.new("RGB", (1, 1))

        def is_loaded(self) -> bool:
            return self.loaded

        def save(self, im: Image.Image, fp: IO[bytes], filename: str) -> None:
            self.saved = True

    handler = TestHandler()
    GribStubImagePlugin.register_handler(handler)
    with Image.open(TEST_FILE) as im:
        assert handler.opened
        assert not handler.is_loaded()

        im.load()
        assert handler.is_loaded()

        temp_file = tmp_path / "temp.grib"
        im.save(temp_file)
        assert handler.saved

    GribStubImagePlugin.register_handler(None)
