from __future__ import annotations

import tempfile
import warnings
from io import BytesIO
from pathlib import Path

import pytest

from PIL import Image, SpiderImagePlugin

from .helper import assert_image_equal, hopper, is_pypy

TEST_FILE = "Tests/images/hopper.spider"


def test_sanity() -> None:
    with Image.open(TEST_FILE) as im:
        im.load()
        assert im.mode == "F"
        assert im.size == (128, 128)
        assert im.format == "SPIDER"


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open_test_image() -> None:
        im = Image.open(TEST_FILE)
        im.load()

    with pytest.warns(ResourceWarning):
        open_test_image()


def test_closed_file() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        im = Image.open(TEST_FILE)
        im.load()
        im.close()


def test_context_manager() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        with Image.open(TEST_FILE) as im:
            im.load()


def test_save(tmp_path: Path) -> None:
    # Arrange
    temp = tmp_path / "temp.spider"
    im = hopper()

    # Act
    im.save(temp, "SPIDER")

    # Assert
    with Image.open(temp) as im2:
        assert im2.mode == "F"
        assert im2.size == (128, 128)
        assert im2.format == "SPIDER"


def test_tempfile() -> None:
    # Arrange
    im = hopper()

    # Act
    with tempfile.TemporaryFile() as fp:
        im.save(fp, "SPIDER")

        # Assert
        fp.seek(0)
        with Image.open(fp) as reloaded:
            assert reloaded.mode == "F"
            assert reloaded.size == (128, 128)
            assert reloaded.format == "SPIDER"


def test_is_spider_image() -> None:
    assert SpiderImagePlugin.isSpiderImage(TEST_FILE)


def test_tell() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        # Act
        index = im.tell()

        # Assert
        assert index == 0


def test_n_frames() -> None:
    with Image.open(TEST_FILE) as im:
        assert isinstance(im, SpiderImagePlugin.SpiderImageFile)
        assert im.n_frames == 1
        assert not im.is_animated


def test_load_image_series() -> None:
    # Arrange
    not_spider_file = "Tests/images/hopper.ppm"
    file_list = [TEST_FILE, not_spider_file, "path/not_found.ext"]

    # Act
    img_list = SpiderImagePlugin.loadImageSeries(file_list)

    # Assert
    assert img_list is not None
    assert len(img_list) == 1
    assert isinstance(img_list[0], Image.Image)
    assert img_list[0].size == (128, 128)


def test_load_image_series_no_input() -> None:
    # Arrange
    file_list = None

    # Act
    img_list = SpiderImagePlugin.loadImageSeries(file_list)

    # Assert
    assert img_list is None


def test_is_int_not_a_number() -> None:
    # Arrange
    not_a_number = "a"

    # Act
    ret = SpiderImagePlugin.isInt(not_a_number)

    # Assert
    assert ret == 0


def test_invalid_file() -> None:
    invalid_file = "Tests/images/invalid.spider"

    with pytest.raises(OSError):
        with Image.open(invalid_file):
            pass


def test_nonstack_file() -> None:
    with Image.open(TEST_FILE) as im:
        with pytest.raises(EOFError):
            im.seek(0)


def test_nonstack_dos() -> None:
    with Image.open(TEST_FILE) as im:
        with pytest.raises(EOFError):
            im.seek(0)


# for issue #4093
def test_odd_size() -> None:
    data = BytesIO()
    width = 100
    im = Image.new("F", (width, 64))
    im.save(data, format="SPIDER")

    data.seek(0)
    with Image.open(data) as im2:
        assert_image_equal(im, im2)
