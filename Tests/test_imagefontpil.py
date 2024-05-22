from __future__ import annotations

import struct
from io import BytesIO

import pytest

from PIL import Image, ImageDraw, ImageFont, _util, features

from .helper import assert_image_equal_tofile

original_core = ImageFont.core


def setup_module() -> None:
    if features.check_module("freetype2"):
        ImageFont.core = _util.DeferredError(ImportError)


def teardown_module() -> None:
    ImageFont.core = original_core


def test_default_font() -> None:
    # Arrange
    txt = 'This is a "better than nothing" default font.'
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Act
    default_font = ImageFont.load_default()
    draw.text((10, 10), txt, font=default_font)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/default_font.png")


def test_size_without_freetype() -> None:
    with pytest.raises(ImportError):
        ImageFont.load_default(size=14)


def test_unicode() -> None:
    # should not segfault, should return UnicodeDecodeError
    # issue #2826
    font = ImageFont.load_default()
    with pytest.raises(UnicodeEncodeError):
        font.getbbox("’")


def test_textbbox() -> None:
    im = Image.new("RGB", (200, 200))
    d = ImageDraw.Draw(im)
    default_font = ImageFont.load_default()
    assert d.textlength("test", font=default_font) == 24
    assert d.textbbox((0, 0), "test", font=default_font) == (0, 0, 24, 11)


def test_decompression_bomb() -> None:
    glyph = struct.pack(">hhhhhhhhhh", 1, 0, 0, 0, 256, 256, 0, 0, 256, 256)
    fp = BytesIO(b"PILfont\n\nDATA\n" + glyph * 256)

    font = ImageFont.ImageFont()
    font._load_pilfont_data(fp, Image.new("L", (256, 256)))
    with pytest.raises(Image.DecompressionBombError):
        font.getmask("A" * 1_000_000)


@pytest.mark.timeout(4)
def test_oom() -> None:
    glyph = struct.pack(
        ">hhhhhhhhhh", 1, 0, -32767, -32767, 32767, 32767, -32767, -32767, 32767, 32767
    )
    fp = BytesIO(b"PILfont\n\nDATA\n" + glyph * 256)

    font = ImageFont.ImageFont()
    font._load_pilfont_data(fp, Image.new("L", (1, 1)))
    font.getmask("A" * 1_000_000)
