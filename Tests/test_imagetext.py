from __future__ import annotations

import pytest

from PIL import Image, ImageDraw, ImageFont, ImageText, features

from .helper import assert_image_similar_tofile, skip_unless_feature

FONT_PATH = "Tests/fonts/FreeMono.ttf"


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(ImageFont.Layout.BASIC),
        pytest.param(ImageFont.Layout.RAQM, marks=skip_unless_feature("raqm")),
    ],
)
def layout_engine(request: pytest.FixtureRequest) -> ImageFont.Layout:
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        None,
        pytest.param(ImageFont.Layout.BASIC, marks=skip_unless_feature("freetype2")),
        pytest.param(ImageFont.Layout.RAQM, marks=skip_unless_feature("raqm")),
    ],
)
def font(
    request: pytest.FixtureRequest,
) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    layout_engine = request.param
    if layout_engine is None:
        return ImageFont.load_default_imagefont()
    else:
        return ImageFont.truetype(FONT_PATH, 20, layout_engine=layout_engine)


def test_get_length(font: ImageFont.ImageFont | ImageFont.FreeTypeFont) -> None:
    factor = 1 if isinstance(font, ImageFont.ImageFont) else 2
    assert ImageText.Text("A", font).get_length() == 6 * factor
    assert ImageText.Text("AB", font).get_length() == 12 * factor
    assert ImageText.Text("M", font).get_length() == 6 * factor
    assert ImageText.Text("y", font).get_length() == 6 * factor
    assert ImageText.Text("a", font).get_length() == 6 * factor

    text = ImageText.Text("\n", font)
    with pytest.raises(ValueError, match="can't measure length of multiline text"):
        text.get_length()


@pytest.mark.parametrize(
    "text, expected",
    (
        ("A", (0, 4, 12, 16)),
        ("AB", (0, 4, 24, 16)),
        ("M", (0, 4, 12, 16)),
        ("y", (0, 7, 12, 20)),
        ("a", (0, 7, 12, 16)),
    ),
)
def test_get_bbox(
    font: ImageFont.ImageFont | ImageFont.FreeTypeFont,
    text: str,
    expected: tuple[int, int, int, int],
) -> None:
    if isinstance(font, ImageFont.ImageFont):
        expected = (0, 0, expected[2] // 2, 11)
    assert ImageText.Text(text, font).get_bbox() == expected


def test_standard_embedded_color(layout_engine: ImageFont.Layout) -> None:
    if features.check_module("freetype2"):
        font = ImageFont.truetype(FONT_PATH, 40, layout_engine=layout_engine)
        text = ImageText.Text("Hello World!", font)
        text.embed_color()
        assert text.get_length() == 288

        im = Image.new("RGB", (300, 64), "white")
        draw = ImageDraw.Draw(im)
        draw.text((10, 10), text, "#fa6")

        assert_image_similar_tofile(im, "Tests/images/standard_embedded.png", 3.1)

    text = ImageText.Text("", mode="1")
    with pytest.raises(
        ValueError, match="Embedded color supported only in RGB and RGBA modes"
    ):
        text.embed_color()


@skip_unless_feature("freetype2")
def test_stroke() -> None:
    for suffix, stroke_fill in {"same": None, "different": "#0f0"}.items():
        # Arrange
        im = Image.new("RGB", (120, 130))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(FONT_PATH, 120)
        text = ImageText.Text("A", font)
        text.stroke(2, stroke_fill)

        # Act
        draw.text((12, 12), text, "#f00")

        # Assert
        assert_image_similar_tofile(
            im, "Tests/images/imagedraw_stroke_" + suffix + ".png", 3.1
        )


def test_wrap() -> None:
    # No wrap required
    text = ImageText.Text("Hello World!")
    text.wrap(100)
    assert text.text == "Hello World!"

    # Wrap word to a new line
    text = ImageText.Text("Hello World!")
    text.wrap(50)
    assert text.text == "Hello\nWorld!"

    # Split word across lines
    text = ImageText.Text("Hello World!")
    text.wrap(25)
    assert text.text == "Hello\nWorl\nd!"
