import pytest

from PIL import Image, ImageDraw, ImageFont, features

from .helper import assert_image_equal_tofile

pytestmark = pytest.mark.skipif(
    features.check_module("freetype2"),
    reason="PILfont superseded if FreeType is supported",
)


def test_default_font():
    # Arrange
    txt = 'This is a "better than nothing" default font.'
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Act
    default_font = ImageFont.load_default()
    draw.text((10, 10), txt, font=default_font)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/default_font.png")


def test_size_without_freetype():
    with pytest.raises(ImportError):
        ImageFont.load_default(size=14)


def test_unicode():
    # should not segfault, should return UnicodeDecodeError
    # issue #2826
    font = ImageFont.load_default()
    with pytest.raises(UnicodeEncodeError):
        font.getbbox("’")


def test_textbbox():
    im = Image.new("RGB", (200, 200))
    d = ImageDraw.Draw(im)
    default_font = ImageFont.load_default()
    assert d.textlength("test", font=default_font) == 24
    assert d.textbbox((0, 0), "test", font=default_font) == (0, 0, 24, 11)
