from __future__ import annotations

import os.path

import pytest

from PIL import Image, ImageDraw, ImageDraw2, features
from PIL._typing import Coords

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
DEFAULT_MODE = "RGB"
IMAGES_PATH = os.path.join("Tests", "images", "imagedraw")

# Image size
W, H = 100, 100

# Bounding box points
X0 = int(W / 4)
X1 = int(X0 * 3)
Y0 = int(H / 4)
Y1 = int(X0 * 3)

# Bounding boxes
BBOX = (((X0, Y0), (X1, Y1)), [(X0, Y0), (X1, Y1)], (X0, Y0, X1, Y1), [X0, Y0, X1, Y1])

# Coordinate sequences
POINTS = (
    ((10, 10), (20, 40), (30, 30)),
    [(10, 10), (20, 40), (30, 30)],
    (10, 10, 20, 40, 30, 30),
    [10, 10, 20, 40, 30, 30],
)

FONT_PATH = "Tests/fonts/FreeMono.ttf"


def test_sanity() -> None:
    im = hopper("RGB").copy()

    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("blue", width=7)
    draw.line(list(range(10)), pen)

    draw2, handler = ImageDraw.getdraw(im)
    assert draw2 is not None
    pen = ImageDraw2.Pen("blue", width=7)
    draw2.line(list(range(10)), pen)


def test_mode() -> None:
    draw = ImageDraw2.Draw("L", (1, 1))
    assert draw.image.mode == "L"

    with pytest.raises(ValueError):
        ImageDraw2.Draw("L")


@pytest.mark.parametrize("bbox", BBOX)
@pytest.mark.parametrize("start, end", ((0, 180), (0.5, 180.4)))
def test_arc(bbox: Coords, start: float, end: float) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("white", width=1)

    # Act
    draw.arc(bbox, pen, start, end)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_chord(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("yellow")
    brush = ImageDraw2.Brush("red")

    # Act
    draw.chord(bbox, pen, 0, 180, brush)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_chord_RGB.png", 1)


@pytest.mark.parametrize("bbox", BBOX)
def test_ellipse(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("blue", width=2)
    brush = ImageDraw2.Brush("green")

    # Act
    draw.ellipse(bbox, pen, brush)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_RGB.png", 1)


def test_ellipse_edge() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    brush = ImageDraw2.Brush("white")

    # Act
    draw.ellipse(((0, 0), (W - 1, H - 1)), brush)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_edge.png", 1)


@pytest.mark.parametrize("points", POINTS)
def test_line(points: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("yellow", width=2)

    # Act
    draw.line(points, pen)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_line.png")


@pytest.mark.parametrize("points", POINTS)
def test_line_pen_as_brush(points: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = None
    brush = ImageDraw2.Pen("yellow", width=2)

    # Act
    # Pass in the pen as the brush parameter
    draw.line(points, pen, brush)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_line.png")


@pytest.mark.parametrize("bbox", BBOX)
@pytest.mark.parametrize("start, end", ((-92, 46), (-92.2, 46.2)))
def test_pieslice(bbox: Coords, start: float, end: float) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("blue")
    brush = ImageDraw2.Brush("white")

    # Act
    draw.pieslice(bbox, pen, start, end, brush)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_pieslice.png", 1)


@pytest.mark.parametrize("points", POINTS)
def test_polygon(points: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("blue", width=2)
    brush = ImageDraw2.Brush("red")

    # Act
    draw.polygon(points, pen, brush)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_polygon.png")


@pytest.mark.parametrize("bbox", BBOX)
def test_rectangle(bbox: Coords) -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("green", width=2)
    brush = ImageDraw2.Brush("black")

    # Act
    draw.rectangle(bbox, pen, brush)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_rectangle.png")


def test_big_rectangle() -> None:
    # Test drawing a rectangle bigger than the image
    # Arrange
    im = Image.new("RGB", (W, H))
    bbox = [(-1, -1), (W + 1, H + 1)]
    brush = ImageDraw2.Brush("orange")
    draw = ImageDraw2.Draw(im)
    expected = "Tests/images/imagedraw_big_rectangle.png"

    # Act
    draw.rectangle(bbox, brush)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


@skip_unless_feature("freetype2")
def test_text() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    font = ImageDraw2.Font("white", FONT_PATH)
    expected = "Tests/images/imagedraw2_text.png"

    # Act
    draw.text((5, 5), "ImageDraw2", font)

    # Assert
    assert_image_similar_tofile(im, expected, 13)


@skip_unless_feature("freetype2")
def test_textbbox() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    font = ImageDraw2.Font("white", FONT_PATH)

    # Act
    bbox = draw.textbbox((0, 0), "ImageDraw2", font)

    # Assert
    right = 72 if features.check_feature("raqm") else 70
    assert bbox == (0, 2, right, 12)


@skip_unless_feature("freetype2")
def test_textsize_empty_string() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    font = ImageDraw2.Font("white", FONT_PATH)

    # Act
    # Should not cause 'SystemError: <built-in method getsize of
    # ImagingFont object at 0x...> returned NULL without setting an error'
    draw.textbbox((0, 0), "", font)
    draw.textbbox((0, 0), "\n", font)
    draw.textbbox((0, 0), "test\n", font)
    draw.textlength("", font)


@skip_unless_feature("freetype2")
def test_flush() -> None:
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    font = ImageDraw2.Font("white", FONT_PATH)

    # Act
    draw.text((5, 5), "ImageDraw2", font)
    im2 = draw.flush()

    # Assert
    assert_image_equal(im, im2)
