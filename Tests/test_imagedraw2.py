import os.path

from PIL import Image, ImageDraw, ImageDraw2

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

# Two kinds of bounding box
BBOX1 = [(X0, Y0), (X1, Y1)]
BBOX2 = [X0, Y0, X1, Y1]

# Two kinds of coordinate sequences
POINTS1 = [(10, 10), (20, 40), (30, 30)]
POINTS2 = [10, 10, 20, 40, 30, 30]

KITE_POINTS = [(10, 50), (70, 10), (90, 50), (70, 90), (10, 50)]

FONT_PATH = "Tests/fonts/FreeMono.ttf"


def test_sanity():
    im = hopper("RGB").copy()

    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("blue", width=7)
    draw.line(list(range(10)), pen)

    draw, handler = ImageDraw.getdraw(im)
    pen = ImageDraw2.Pen("blue", width=7)
    draw.line(list(range(10)), pen)


def helper_ellipse(mode, bbox):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("blue", width=2)
    brush = ImageDraw2.Brush("green")
    expected = f"Tests/images/imagedraw_ellipse_{mode}.png"

    # Act
    draw.ellipse(bbox, pen, brush)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


def test_ellipse1():
    helper_ellipse("RGB", BBOX1)


def test_ellipse2():
    helper_ellipse("RGB", BBOX2)


def test_ellipse_edge():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    brush = ImageDraw2.Brush("white")

    # Act
    draw.ellipse(((0, 0), (W - 1, H - 1)), brush)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_edge.png", 1)


def helper_line(points):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("yellow", width=2)

    # Act
    draw.line(points, pen)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_line.png")


def test_line1_pen():
    helper_line(POINTS1)


def test_line2_pen():
    helper_line(POINTS2)


def test_line_pen_as_brush():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = None
    brush = ImageDraw2.Pen("yellow", width=2)

    # Act
    # Pass in the pen as the brush parameter
    draw.line(POINTS1, pen, brush)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_line.png")


def helper_polygon(points):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("blue", width=2)
    brush = ImageDraw2.Brush("red")

    # Act
    draw.polygon(points, pen, brush)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_polygon.png")


def test_polygon1():
    helper_polygon(POINTS1)


def test_polygon2():
    helper_polygon(POINTS2)


def helper_rectangle(bbox):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    pen = ImageDraw2.Pen("green", width=2)
    brush = ImageDraw2.Brush("black")

    # Act
    draw.rectangle(bbox, pen, brush)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/imagedraw_rectangle.png")


def test_rectangle1():
    helper_rectangle(BBOX1)


def test_rectangle2():
    helper_rectangle(BBOX2)


def test_big_rectangle():
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
def test_text():
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
def test_textsize():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    font = ImageDraw2.Font("white", FONT_PATH)

    # Act
    size = draw.textsize("ImageDraw2", font)

    # Assert
    assert size[1] == 12


@skip_unless_feature("freetype2")
def test_textsize_empty_string():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    font = ImageDraw2.Font("white", FONT_PATH)

    # Act
    # Should not cause 'SystemError: <built-in method getsize of
    # ImagingFont object at 0x...> returned NULL without setting an error'
    draw.textsize("", font)
    draw.textsize("\n", font)
    draw.textsize("test\n", font)


@skip_unless_feature("freetype2")
def test_flush():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw2.Draw(im)
    font = ImageDraw2.Font("white", FONT_PATH)

    # Act
    draw.text((5, 5), "ImageDraw2", font)
    im2 = draw.flush()

    # Assert
    assert_image_equal(im, im2)
