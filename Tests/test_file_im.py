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
    with pytest.warns(DeprecationWarning, match="IM image format"):
        im = Image.open(TEST_IM)
    im.load()
    assert im.mode == "RGB"
    assert im.size == (128, 128)
    assert im.format == "IM"
    im.close()


def test_name_limit(tmp_path: Path) -> None:
    out = tmp_path / ("name_limit_test" * 7 + ".im")
    with pytest.warns(DeprecationWarning, match="IM image format"):
        with Image.open(TEST_IM) as im:
            im.save(out)
    assert filecmp.cmp(out, "Tests/images/hopper_long_name.im")


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open_test_image() -> None:
        with pytest.warns(DeprecationWarning, match="IM image format"):
            im = Image.open(TEST_IM)
        im.load()

    with pytest.warns(ResourceWarning):
        open_test_image()


def test_closed_file() -> None:
    with warnings.catch_warnings(action="error"):
        with pytest.warns(DeprecationWarning, match="IM image format"):
            im = Image.open(TEST_IM)
        im.load()
        im.close()


def test_context_manager() -> None:
    with warnings.catch_warnings(action="error"):
        with pytest.warns(DeprecationWarning, match="IM image format"):
            with Image.open(TEST_IM) as im:
                im.load()


def test_tell() -> None:
    # Arrange
    with pytest.warns(DeprecationWarning, match="IM image format"):
        with Image.open(TEST_IM) as im:
            # Act
            frame = im.tell()

    # Assert
    assert frame == 0


def test_n_frames() -> None:
    with pytest.warns(DeprecationWarning, match="IM image format"):
        im = Image.open(TEST_IM)
    assert isinstance(im, ImImagePlugin.ImImageFile)
    assert im.n_frames == 1
    assert not im.is_animated
    im.close()


def test_eoferror() -> None:
    with pytest.warns(DeprecationWarning, match="IM image format"):
        im = Image.open(TEST_IM)
    assert isinstance(im, ImImagePlugin.ImImageFile)
    n_frames = im.n_frames

    # Test seeking past the last frame
    with pytest.raises(EOFError):
        im.seek(n_frames)
    assert im.tell() < n_frames

    # Test that seeking to the last frame does not raise an error
    im.seek(n_frames - 1)
    im.close()


@pytest.mark.parametrize("mode", ("RGB", "P", "PA"))
def test_roundtrip(mode: str, tmp_path: Path) -> None:
    out = tmp_path / "temp.im"
    im = hopper(mode)
    with pytest.warns(DeprecationWarning, match="IM image format"):
        im.save(out)
    with pytest.warns(DeprecationWarning, match="IM image format"):
        assert_image_equal_tofile(im, out)


def test_small_palette(tmp_path: Path) -> None:
    im = Image.new("P", (1, 1))
    colors = [0, 1, 2]
    im.putpalette(colors)

    out = tmp_path / "temp.im"
    with pytest.warns(DeprecationWarning, match="IM image format"):
        im.save(out)

    with pytest.warns(DeprecationWarning, match="IM image format"):
        reloaded = Image.open(out)
    assert reloaded.getpalette() == colors + [0] * 765
    reloaded.close()


def test_save_unsupported_mode(tmp_path: Path) -> None:
    out = tmp_path / "temp.im"
    im = hopper("HSV")
    with pytest.raises(ValueError):
        with pytest.warns(DeprecationWarning, match="IM image format"):
            im.save(out)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        ImImagePlugin.ImImageFile(invalid_file)


def test_number() -> None:
    with pytest.warns(DeprecationWarning, match="IM image format"):
        assert ImImagePlugin.number("1.2") == 1.2
