from __future__ import annotations

import warnings

import unittest
from unittest.mock import patch, MagicMock

import pytest

from PIL import FliImagePlugin, Image, ImageFile

from .helper import assert_image_equal, assert_image_equal_tofile, is_pypy

# created as an export of a palette image from Gimp2.6
# save as...-> hopper.fli, default options.
static_test_file = "Tests/images/hopper.fli"

# From https://samples.ffmpeg.org/fli-flc/
animated_test_file = "Tests/images/a.fli"

# From https://samples.ffmpeg.org/fli-flc/
animated_test_file_with_prefix_chunk = "Tests/images/2422.flc"


def test_sanity() -> None:
    with Image.open(static_test_file) as im:
        im.load()
        assert im.mode == "P"
        assert im.size == (128, 128)
        assert im.format == "FLI"
        assert not im.is_animated

    with Image.open(animated_test_file) as im:
        assert im.mode == "P"
        assert im.size == (320, 200)
        assert im.format == "FLI"
        assert im.info["duration"] == 71
        assert im.is_animated


def test_prefix_chunk() -> None:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    try:
        with Image.open(animated_test_file_with_prefix_chunk) as im:
            assert im.mode == "P"
            assert im.size == (320, 200)
            assert im.format == "FLI"
            assert im.info["duration"] == 171
            assert im.is_animated

            palette = im.getpalette()
            assert palette[3:6] == [255, 255, 255]
            assert palette[381:384] == [204, 204, 12]
            assert palette[765:] == [252, 0, 0]
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open() -> None:
        im = Image.open(static_test_file)
        im.load()

    with pytest.warns(ResourceWarning):
        open()


def test_closed_file() -> None:
    with warnings.catch_warnings():
        im = Image.open(static_test_file)
        im.load()
        im.close()


def test_seek_after_close() -> None:
    im = Image.open(animated_test_file)
    im.seek(1)
    im.close()

    with pytest.raises(ValueError):
        im.seek(0)


def test_context_manager() -> None:
    with warnings.catch_warnings():
        with Image.open(static_test_file) as im:
            im.load()


def test_tell() -> None:
    # Arrange
    with Image.open(static_test_file) as im:
        # Act
        frame = im.tell()

        # Assert
        assert frame == 0


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        FliImagePlugin.FliImageFile(invalid_file)


def test_palette_chunk_second() -> None:
    with Image.open("Tests/images/hopper_palette_chunk_second.fli") as im:
        with Image.open(static_test_file) as expected:
            assert_image_equal(im.convert("RGB"), expected.convert("RGB"))


def test_n_frames() -> None:
    with Image.open(static_test_file) as im:
        assert im.n_frames == 1
        assert not im.is_animated

    with Image.open(animated_test_file) as im:
        assert im.n_frames == 384
        assert im.is_animated


def test_eoferror() -> None:
    with Image.open(animated_test_file) as im:
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_seek_tell() -> None:
    with Image.open(animated_test_file) as im:
        layer_number = im.tell()
        assert layer_number == 0

        im.seek(0)
        layer_number = im.tell()
        assert layer_number == 0

        im.seek(1)
        layer_number = im.tell()
        assert layer_number == 1

        im.seek(2)
        layer_number = im.tell()
        assert layer_number == 2

        im.seek(1)
        layer_number = im.tell()
        assert layer_number == 1


def test_seek() -> None:
    with Image.open(animated_test_file) as im:
        im.seek(50)

        assert_image_equal_tofile(im, "Tests/images/a_fli.png")


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/timeout-9139147ce93e20eb14088fe238e541443ffd64b3.fli",
        "Tests/images/timeout-bff0a9dc7243a8e6ede2408d2ffa6a9964698b87.fli",
    ],
)
@pytest.mark.timeout(timeout=3)
def test_timeouts(test_file: str) -> None:
    with open(test_file, "rb") as f:
        with Image.open(f) as im:
            with pytest.raises(OSError):
                im.load()


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/crash-5762152299364352.fli",
    ],
)
def test_crash(test_file: str) -> None:
    with open(test_file, "rb") as f:
        with Image.open(f) as im:
            with pytest.raises(OSError):
                im.load()
