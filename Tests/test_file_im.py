from __future__ import annotations

import filecmp
import warnings
from pathlib import Path

import pytest

from PIL import Image, ImImagePlugin

from .helper import assert_image_equal_tofile, hopper, is_pypy

# sample im
TEST_IM = "Tests/images/hopper.im"


def test_sanity() -> None:
    with Image.open(TEST_IM) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "IM"


def test_name_limit(tmp_path: Path) -> None:
    out = tmp_path / ("name_limit_test" * 7 + ".im")
    with Image.open(TEST_IM) as im:
        im.save(out)
    assert filecmp.cmp(out, "Tests/images/hopper_long_name.im")


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open_test_image() -> None:
        im = Image.open(TEST_IM)
        im.load()

    with pytest.warns(ResourceWarning):
        open_test_image()


def test_closed_file() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        im = Image.open(TEST_IM)
        im.load()
        im.close()


def test_context_manager() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        with Image.open(TEST_IM) as im:
            im.load()


def test_tell() -> None:
    # Arrange
    with Image.open(TEST_IM) as im:
        # Act
        frame = im.tell()

    # Assert
    assert frame == 0


def test_n_frames() -> None:
    with Image.open(TEST_IM) as im:
        assert isinstance(im, ImImagePlugin.ImImageFile)
        assert im.n_frames == 1
        assert not im.is_animated


def test_eoferror() -> None:
    with Image.open(TEST_IM) as im:
        assert isinstance(im, ImImagePlugin.ImImageFile)
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


@pytest.mark.parametrize("mode", ("RGB", "P", "PA"))
def test_roundtrip(mode: str, tmp_path: Path) -> None:
    out = tmp_path / "temp.im"
    im = hopper(mode)
    im.save(out)
    assert_image_equal_tofile(im, out)


def test_small_palette(tmp_path: Path) -> None:
    im = Image.new("P", (1, 1))
    colors = [0, 1, 2]
    im.putpalette(colors)

    out = tmp_path / "temp.im"
    im.save(out)

    with Image.open(out) as reloaded:
        assert reloaded.getpalette() == colors + [0] * 765


def test_save_unsupported_mode(tmp_path: Path) -> None:
    out = tmp_path / "temp.im"
    im = hopper("HSV")
    with pytest.raises(ValueError):
        im.save(out)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        ImImagePlugin.ImImageFile(invalid_file)


def test_number() -> None:
    assert ImImagePlugin.number("1.2") == 1.2
