from __future__ import annotations

import warnings

import pytest

from PIL import DcxImagePlugin, Image

from .helper import assert_image_equal, hopper, is_pypy

# Created with ImageMagick: convert hopper.ppm hopper.dcx
TEST_FILE = "Tests/images/hopper.dcx"


def test_sanity() -> None:
    # Arrange

    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.size == (128, 128)
        assert isinstance(im, DcxImagePlugin.DcxImageFile)
        orig = hopper()
        assert_image_equal(im, orig)


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


def test_invalid_file() -> None:
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            DcxImagePlugin.DcxImageFile(fp)


def test_tell() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        # Act
        frame = im.tell()

        # Assert
        assert frame == 0


def test_n_frames() -> None:
    with Image.open(TEST_FILE) as im:
        assert isinstance(im, DcxImagePlugin.DcxImageFile)
        assert im.n_frames == 1
        assert not im.is_animated


def test_eoferror() -> None:
    with Image.open(TEST_FILE) as im:
        assert isinstance(im, DcxImagePlugin.DcxImageFile)
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_seek_too_far() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        frame = 999  # too big on purpose

    # Act / Assert
    with pytest.raises(EOFError):
        im.seek(frame)
