from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import IO

import pytest

from PIL import Hdf5StubImagePlugin, Image, ImageFile

TEST_FILE = "Tests/images/hdf5.h5"


def test_open() -> None:
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.format == "HDF5"

        # Dummy data from the stub
        assert im.mode == "F"
        assert im.size == (1, 1)


def test_invalid_file() -> None:
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        Hdf5StubImagePlugin.HDF5StubImageFile(invalid_file)


def test_load() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        # Act / Assert: stub cannot load without an implemented handler
        with pytest.raises(OSError):
            im.load()


def test_save() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        dummy_fp = BytesIO()
        dummy_filename = "dummy.h5"

        # Act / Assert: stub cannot save without an implemented handler
        with pytest.raises(OSError):
            im.save(dummy_filename)
        with pytest.raises(OSError):
            Hdf5StubImagePlugin._save(im, dummy_fp, dummy_filename)


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
    Hdf5StubImagePlugin.register_handler(handler)
    with Image.open(TEST_FILE) as im:
        assert handler.opened
        assert not handler.is_loaded()

        im.load()
        assert handler.is_loaded()

        temp_file = tmp_path / "temp.h5"
        im.save(temp_file)
        assert handler.saved

    Hdf5StubImagePlugin.register_handler(None)
