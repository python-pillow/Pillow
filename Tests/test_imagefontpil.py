from __future__ import annotations

import struct
from io import BytesIO

import pytest

from PIL import Image, ImageDraw, ImageFont, _util, features

from .helper import assert_image_equal_tofile, timeout_unless_slower_valgrind

fonts = [ImageFont.load_default_imagefont()]
if not features.check_module("freetype2"):
    default_font = ImageFont.load_default()
    if isinstance(default_font, ImageFont.ImageFont):
        fonts.append(default_font)


@pytest.mark.parametrize("font", fonts)
def test_default_font(font: ImageFont.ImageFont) -> None:
    # Arrange
    txt = 'This is a "better than nothing" default font.'
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Act
    draw.text((10, 10), txt, font=font)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/default_font.png")


def test_without_freetype() -> None:
    original_core = ImageFont.core
    if features.check_module("freetype2"):
        ImageFont.core = _util.DeferredError(ImportError("Disabled for testing"))
    try:
        with pytest.raises(ImportError):
            ImageFont.truetype("Tests/fonts/FreeMono.ttf")

        assert isinstance(ImageFont.load_default(), ImageFont.ImageFont)

        with pytest.raises(ImportError):
            ImageFont.load_default(size=14)
    finally:
        ImageFont.core = original_core


@pytest.mark.parametrize("font", fonts)
def test_unicode(font: ImageFont.ImageFont) -> None:
    # should not segfault, should return UnicodeDecodeError
    # issue #2826
    with pytest.raises(UnicodeEncodeError):
        font.getbbox("’")


@pytest.mark.parametrize("font", fonts)
def test_textbbox(font: ImageFont.ImageFont) -> None:
    im = Image.new("RGB", (200, 200))
    d = ImageDraw.Draw(im)
    assert d.textlength("test", font=font) == 24
    assert d.textbbox((0, 0), "test", font=font) == (0, 0, 24, 11)


def test_decompression_bomb() -> None:
    glyph = struct.pack(">hhhhhhhhhh", 1, 0, 0, 0, 256, 256, 0, 0, 256, 256)
    fp = BytesIO(b"PILfont\n\nDATA\n" + glyph * 256)

    font = ImageFont.ImageFont()
    font._load_pilfont_data(fp, Image.new("L", (256, 256)))
    with pytest.raises(Image.DecompressionBombError):
        font.getmask("A" * 1_000_000)


@timeout_unless_slower_valgrind(4)
def test_oom() -> None:
    glyph = struct.pack(
        ">hhhhhhhhhh", 1, 0, -32767, -32767, 32767, 32767, -32767, -32767, 32767, 32767
    )
    fp = BytesIO(b"PILfont\n\nDATA\n" + glyph * 256)

    font = ImageFont.ImageFont()
    font._load_pilfont_data(fp, Image.new("L", (1, 1)))
    font.getmask("A" * 1_000_000)
