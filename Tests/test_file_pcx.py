from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image, ImageFile, PcxImagePlugin

from .helper import assert_image_equal, hopper


def _roundtrip(tmp_path: Path, im: Image.Image) -> None:
    f = str(tmp_path / "temp.pcx")
    im.save(f)
    with Image.open(f) as im2:
        assert im2.mode == im.mode
        assert im2.size == im.size
        assert im2.format == "PCX"
        assert im2.get_format_mimetype() == "image/x-pcx"
        assert_image_equal(im2, im)


def test_sanity(tmp_path: Path) -> None:
    for mode in ("1", "L", "P", "RGB"):
        _roundtrip(tmp_path, hopper(mode))

    # Test a palette with less than 256 colors
    im = Image.new("P", (1, 1))
    im.putpalette((255, 0, 0))
    _roundtrip(tmp_path, im)

    # Test an unsupported mode
    f = str(tmp_path / "temp.pcx")
    im = hopper("RGBA")
    with pytest.raises(ValueError):
        im.save(f)


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        PcxImagePlugin.PcxImageFile(invalid_file)


@pytest.mark.parametrize("mode", ("1", "L", "P", "RGB"))
def test_odd(tmp_path: Path, mode: str) -> None:
    # See issue #523, odd sized images should have a stride that's even.
    # Not that ImageMagick or GIMP write PCX that way.
    # We were not handling properly.
    # larger, odd sized images are better here to ensure that
    # we handle interrupted scan lines properly.
    _roundtrip(tmp_path, hopper(mode).resize((511, 511)))


def test_odd_read() -> None:
    # Reading an image with an odd stride, making it malformed
    with Image.open("Tests/images/odd_stride.pcx") as im:
        im.load()

        assert im.size == (371, 150)


def test_pil184() -> None:
    # Check reading of files where xmin/xmax is not zero.

    test_file = "Tests/images/pil184.pcx"
    with Image.open(test_file) as im:
        assert im.size == (447, 144)
        assert im.tile[0][1] == (0, 0, 447, 144)

        # Make sure all pixels are either 0 or 255.
        assert im.histogram()[0] + im.histogram()[255] == 447 * 144


def test_1px_width(tmp_path: Path) -> None:
    im = Image.new("L", (1, 256))
    px = im.load()
    assert px is not None
    for y in range(256):
        px[0, y] = y
    _roundtrip(tmp_path, im)


def test_large_count(tmp_path: Path) -> None:
    im = Image.new("L", (256, 1))
    px = im.load()
    assert px is not None
    for x in range(256):
        px[x, 0] = x // 67 * 67
    _roundtrip(tmp_path, im)


def _test_buffer_overflow(tmp_path: Path, im: Image.Image, size: int = 1024) -> None:
    _last = ImageFile.MAXBLOCK
    ImageFile.MAXBLOCK = size
    try:
        _roundtrip(tmp_path, im)
    finally:
        ImageFile.MAXBLOCK = _last


def test_break_in_count_overflow(tmp_path: Path) -> None:
    im = Image.new("L", (256, 5))
    px = im.load()
    assert px is not None
    for y in range(4):
        for x in range(256):
            px[x, y] = x % 128
    _test_buffer_overflow(tmp_path, im)


def test_break_one_in_loop(tmp_path: Path) -> None:
    im = Image.new("L", (256, 5))
    px = im.load()
    assert px is not None
    for y in range(5):
        for x in range(256):
            px[x, y] = x % 128
    _test_buffer_overflow(tmp_path, im)


def test_break_many_in_loop(tmp_path: Path) -> None:
    im = Image.new("L", (256, 5))
    px = im.load()
    assert px is not None
    for y in range(4):
        for x in range(256):
            px[x, y] = x % 128
    for x in range(8):
        px[x, 4] = 16
    _test_buffer_overflow(tmp_path, im)


def test_break_one_at_end(tmp_path: Path) -> None:
    im = Image.new("L", (256, 5))
    px = im.load()
    assert px is not None
    for y in range(5):
        for x in range(256):
            px[x, y] = x % 128
    px[0, 3] = 128 + 64
    _test_buffer_overflow(tmp_path, im)


def test_break_many_at_end(tmp_path: Path) -> None:
    im = Image.new("L", (256, 5))
    px = im.load()
    assert px is not None
    for y in range(5):
        for x in range(256):
            px[x, y] = x % 128
    for x in range(4):
        px[x * 2, 3] = 128 + 64
        px[x + 256 - 4, 3] = 0
    _test_buffer_overflow(tmp_path, im)


def test_break_padding(tmp_path: Path) -> None:
    im = Image.new("L", (257, 5))
    px = im.load()
    assert px is not None
    for y in range(5):
        for x in range(257):
            px[x, y] = x % 128
    for x in range(5):
        px[x, 3] = 0
    _test_buffer_overflow(tmp_path, im)
