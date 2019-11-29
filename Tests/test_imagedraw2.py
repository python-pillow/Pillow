import os.path
import unittest

from PIL import Image, ImageDraw2, features

from .helper import PillowTestCase, hopper

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

HAS_FREETYPE = features.check("freetype2")
FONT_PATH = "Tests/fonts/FreeMono.ttf"


class TestImageDraw(PillowTestCase):
    def test_sanity(self):
        im = hopper("RGB").copy()

        draw = ImageDraw2.Draw(im)
        pen = ImageDraw2.Pen("blue", width=7)
        draw.line(list(range(10)), pen)

        from PIL import ImageDraw

        draw, handler = ImageDraw.getdraw(im)
        pen = ImageDraw2.Pen("blue", width=7)
        draw.line(list(range(10)), pen)

    def helper_ellipse(self, mode, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        pen = ImageDraw2.Pen("blue", width=2)
        brush = ImageDraw2.Brush("green")
        expected = "Tests/images/imagedraw_ellipse_{}.png".format(mode)

        # Act
        draw.ellipse(bbox, pen, brush)

        # Assert
        self.assert_image_similar(im, Image.open(expected), 1)

    def test_ellipse1(self):
        self.helper_ellipse("RGB", BBOX1)

    def test_ellipse2(self):
        self.helper_ellipse("RGB", BBOX2)

    def test_ellipse_edge(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        brush = ImageDraw2.Brush("white")

        # Act
        draw.ellipse(((0, 0), (W - 1, H)), brush)

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_ellipse_edge.png"), 1
        )

    def helper_line(self, points):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        pen = ImageDraw2.Pen("yellow", width=2)

        # Act
        draw.line(points, pen)

        # Assert
        self.assert_image_equal(im, Image.open("Tests/images/imagedraw_line.png"))

    def test_line1_pen(self):
        self.helper_line(POINTS1)

    def test_line2_pen(self):
        self.helper_line(POINTS2)

    def test_line_pen_as_brush(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        pen = None
        brush = ImageDraw2.Pen("yellow", width=2)

        # Act
        # Pass in the pen as the brush parameter
        draw.line(POINTS1, pen, brush)

        # Assert
        self.assert_image_equal(im, Image.open("Tests/images/imagedraw_line.png"))

    def helper_polygon(self, points):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        pen = ImageDraw2.Pen("blue", width=2)
        brush = ImageDraw2.Brush("red")

        # Act
        draw.polygon(points, pen, brush)

        # Assert
        self.assert_image_equal(im, Image.open("Tests/images/imagedraw_polygon.png"))

    def test_polygon1(self):
        self.helper_polygon(POINTS1)

    def test_polygon2(self):
        self.helper_polygon(POINTS2)

    def helper_rectangle(self, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        pen = ImageDraw2.Pen("green", width=2)
        brush = ImageDraw2.Brush("black")

        # Act
        draw.rectangle(bbox, pen, brush)

        # Assert
        self.assert_image_equal(im, Image.open("Tests/images/imagedraw_rectangle.png"))

    def test_rectangle1(self):
        self.helper_rectangle(BBOX1)

    def test_rectangle2(self):
        self.helper_rectangle(BBOX2)

    def test_big_rectangle(self):
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
        self.assert_image_similar(im, Image.open(expected), 1)

    @unittest.skipUnless(HAS_FREETYPE, "ImageFont not available")
    def test_text(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        font = ImageDraw2.Font("white", FONT_PATH)
        expected = "Tests/images/imagedraw2_text.png"

        # Act
        draw.text((5, 5), "ImageDraw2", font)

        # Assert
        self.assert_image_similar(im, Image.open(expected), 13)

    @unittest.skipUnless(HAS_FREETYPE, "ImageFont not available")
    def test_textsize(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        font = ImageDraw2.Font("white", FONT_PATH)

        # Act
        size = draw.textsize("ImageDraw2", font)

        # Assert
        self.assertEqual(size[1], 12)

    @unittest.skipUnless(HAS_FREETYPE, "ImageFont not available")
    def test_textsize_empty_string(self):
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

    @unittest.skipUnless(HAS_FREETYPE, "ImageFont not available")
    def test_flush(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw2.Draw(im)
        font = ImageDraw2.Font("white", FONT_PATH)

        # Act
        draw.text((5, 5), "ImageDraw2", font)
        im2 = draw.flush()

        # Assert
        self.assert_image_equal(im, im2)
