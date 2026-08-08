from __future__ import annotations

import filecmp
import io
import warnings
from pathlib import Path

import pytest

from PIL import Image, ImImagePlugin

from .helper import assert_image_equal, assert_image_equal_tofile, hopper, is_pypy

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
    with warnings.catch_warnings(action="error"):
        im = Image.open(TEST_IM)
        im.load()
        im.close()


def test_context_manager() -> None:
    with warnings.catch_warnings(action="error"):
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


@pytest.mark.parametrize(
    "image_type, rawmode, mode",
    (
        ("L 16", "I;16", "I;16"),
        ("L 32S", "I;32S", "I"),
        ("L 32F", "F;32F", "F"),
        ("YCC", "YCbCr;L", "YCbCr"),
    ),
)
def test_seek_non_8bit(image_type: str, rawmode: str, mode: str) -> None:
    # The frame stride must be derived from the actual bytes per pixel, not
    # from the length of the mode name (which only matches for 8-bit bands).
    w, h = 4, 4
    frames = []
    for base in (0, 1000):
        frame = Image.new(mode, (w, h))
        for y in range(h):
            for x in range(w):
                frame.putpixel((x, y), base + y * w + x)
        frames.append(frame)

    header = (
        f"Image type: {image_type} image\r\n"
        f"Image size (x*y): {w}*{h}\r\n"
        f"File size (no of images): {len(frames)}\r\n"
    ).encode("ascii")
    header += b"\x00" * (511 - len(header)) + b"\x1a"
    data = b"".join(frame.tobytes("raw", rawmode, 0, -1) for frame in frames)

    with Image.open(io.BytesIO(header + data)) as im:
        for index, frame in enumerate(frames):
            im.seek(index)
            assert_image_equal(im, frame)


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
