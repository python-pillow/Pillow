from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
import os.path

import sys

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
DEFAULT_MODE = 'RGB'
IMAGES_PATH = os.path.join('Tests', 'images', 'imagedraw')

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


class TestImageDraw(PillowTestCase):

    def test_sanity(self):
        im = hopper("RGB").copy()

        draw = ImageDraw.ImageDraw(im)
        draw = ImageDraw.Draw(im)

        draw.ellipse(list(range(4)))
        draw.line(list(range(10)))
        draw.polygon(list(range(100)))
        draw.rectangle(list(range(4)))

    def test_valueerror(self):
        im = Image.open("Tests/images/chi.gif")

        draw = ImageDraw.Draw(im)
        draw.line(((0, 0)), fill=(0, 0, 0))

    def test_mode_mismatch(self):
        im = hopper("RGB").copy()

        self.assertRaises(ValueError, ImageDraw.ImageDraw, im, mode="L")

    def helper_arc(self, bbox, start, end):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.arc(bbox, start, end)

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_arc.png"), 1)

    def test_arc1(self):
        self.helper_arc(BBOX1, 0, 180)
        self.helper_arc(BBOX1, 0.5, 180.4)

    def test_arc2(self):
        self.helper_arc(BBOX2, 0, 180)
        self.helper_arc(BBOX2, 0.5, 180.4)

    def test_arc_end_le_start(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)
        start = 270.5
        end = 0

        # Act
        draw.arc(BBOX1, start=start, end=end)

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_arc_end_le_start.png"))

    def test_arc_no_loops(self):
        # No need to go in loops
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)
        start = 5
        end = 370

        # Act
        draw.arc(BBOX1, start=start, end=end)

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_arc_no_loops.png"), 1)

    def test_bitmap(self):
        # Arrange
        small = Image.open("Tests/images/pil123rgba.png").resize((50, 50))
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.bitmap((10, 10), small)

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_bitmap.png"))

    def helper_chord(self, mode, bbox, start, end):
        # Arrange
        im = Image.new(mode, (W, H))
        draw = ImageDraw.Draw(im)
        expected = "Tests/images/imagedraw_chord_{}.png".format(mode)

        # Act
        draw.chord(bbox, start, end, fill="red", outline="yellow")

        # Assert
        self.assert_image_similar(im, Image.open(expected), 1)

    def test_chord1(self):
        for mode in ["RGB", "L"]:
            self.helper_chord(mode, BBOX1, 0, 180)
            self.helper_chord(mode, BBOX1, 0.5, 180.4)

    def test_chord2(self):
        for mode in ["RGB", "L"]:
            self.helper_chord(mode, BBOX2, 0, 180)
            self.helper_chord(mode, BBOX2, 0.5, 180.4)

    def helper_ellipse(self, mode, bbox):
        # Arrange
        im = Image.new(mode, (W, H))
        draw = ImageDraw.Draw(im)
        expected = "Tests/images/imagedraw_ellipse_{}.png".format(mode)

        # Act
        draw.ellipse(bbox, fill="green", outline="blue")

        # Assert
        self.assert_image_similar(im, Image.open(expected), 1)

    def test_ellipse1(self):
        for mode in ["RGB", "L"]:
            self.helper_ellipse(mode, BBOX1)

    def test_ellipse2(self):
        for mode in ["RGB", "L"]:
            self.helper_ellipse(mode, BBOX2)

    def test_ellipse_edge(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.ellipse(((0, 0), (W-1, H)), fill="white")

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_ellipse_edge.png"), 1)

    def helper_line(self, points):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.line(points, fill="yellow", width=2)

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_line.png"))

    def test_line1(self):
        self.helper_line(POINTS1)

    def test_line2(self):
        self.helper_line(POINTS2)

    def test_shape1(self):
        # Arrange
        im = Image.new("RGB", (100, 100), "white")
        draw = ImageDraw.Draw(im)
        x0, y0 = 5, 5
        x1, y1 = 5, 50
        x2, y2 = 95, 50
        x3, y3 = 95, 5

        # Act
        s = ImageDraw.Outline()
        s.move(x0, y0)
        s.curve(x1, y1, x2, y2, x3, y3)
        s.line(x0, y0)

        draw.shape(s, fill=1)

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_shape1.png"))

    def test_shape2(self):
        # Arrange
        im = Image.new("RGB", (100, 100), "white")
        draw = ImageDraw.Draw(im)
        x0, y0 = 95, 95
        x1, y1 = 95, 50
        x2, y2 = 5, 50
        x3, y3 = 5, 95

        # Act
        s = ImageDraw.Outline()
        s.move(x0, y0)
        s.curve(x1, y1, x2, y2, x3, y3)
        s.line(x0, y0)

        draw.shape(s, outline="blue")

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_shape2.png"))

    def helper_pieslice(self, bbox, start, end):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.pieslice(bbox, start, end, fill="white", outline="blue")

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_pieslice.png"), 1)

    def test_pieslice1(self):
        self.helper_pieslice(BBOX1, -90, 45)
        self.helper_pieslice(BBOX1, -90.5, 45.4)

    def test_pieslice2(self):
        self.helper_pieslice(BBOX2, -90, 45)
        self.helper_pieslice(BBOX2, -90.5, 45.4)

    def helper_point(self, points):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.point(points, fill="yellow")

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_point.png"))

    def test_point1(self):
        self.helper_point(POINTS1)

    def test_point2(self):
        self.helper_point(POINTS2)

    def helper_polygon(self, points):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.polygon(points, fill="red", outline="blue")

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_polygon.png"))

    def test_polygon1(self):
        self.helper_polygon(POINTS1)

    def test_polygon2(self):
        self.helper_polygon(POINTS2)

    def test_polygon_kite(self):
        # Test drawing lines of different gradients (dx>dy, dy>dx) and
        # vertical (dx==0) and horizontal (dy==0) lines
        for mode in ["RGB", "L"]:
            # Arrange
            im = Image.new(mode, (W, H))
            draw = ImageDraw.Draw(im)
            expected = "Tests/images/imagedraw_polygon_kite_{}.png".format(
                mode)

            # Act
            draw.polygon(KITE_POINTS, fill="blue", outline="yellow")

            # Assert
            self.assert_image_equal(im, Image.open(expected))

    def helper_rectangle(self, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.rectangle(bbox, fill="black", outline="green")

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_rectangle.png"))

    def test_rectangle1(self):
        self.helper_rectangle(BBOX1)

    def test_rectangle2(self):
        self.helper_rectangle(BBOX2)

    def test_big_rectangle(self):
        # Test drawing a rectangle bigger than the image
        # Arrange
        im = Image.new("RGB", (W, H))
        bbox = [(-1, -1), (W+1, H+1)]
        draw = ImageDraw.Draw(im)
        expected = "Tests/images/imagedraw_big_rectangle.png"

        # Act
        draw.rectangle(bbox, fill="orange")

        # Assert
        self.assert_image_similar(im, Image.open(expected), 1)

    def test_floodfill(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)
        draw.rectangle(BBOX2, outline="yellow", fill="green")
        centre_point = (int(W/2), int(H/2))
        red = ImageColor.getrgb("red")
        im_floodfill = Image.open("Tests/images/imagedraw_floodfill.png")

        # Act
        ImageDraw.floodfill(im, centre_point, red)

        # Assert
        self.assert_image_equal(im, im_floodfill)

        # Test that using the same colour does not change the image
        ImageDraw.floodfill(im, centre_point, red)
        self.assert_image_equal(im, im_floodfill)

        # Test that filling outside the image does not change the image
        ImageDraw.floodfill(im, (W, H), red)
        self.assert_image_equal(im, im_floodfill)

    @unittest.skipIf(hasattr(sys, 'pypy_version_info'),
                     "Causes fatal RPython error on PyPy")
    def test_floodfill_border(self):
        # floodfill() is experimental

        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)
        draw.rectangle(BBOX2, outline="yellow", fill="green")
        centre_point = (int(W/2), int(H/2))

        # Act
        ImageDraw.floodfill(
            im, centre_point, ImageColor.getrgb("red"),
            border=ImageColor.getrgb("black"))

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_floodfill2.png"))


    def test_floodfill_thresh(self):
        # floodfill() is experimental

        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)
        draw.rectangle(BBOX2, outline="darkgreen", fill="green")
        centre_point = (int(W/2), int(H/2))

        # Act
        ImageDraw.floodfill(
            im, centre_point, ImageColor.getrgb("red"),
            thresh=30)

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_floodfill2.png"))

    def create_base_image_draw(self, size,
                               mode=DEFAULT_MODE,
                               background1=WHITE,
                               background2=GRAY):
        img = Image.new(mode, size, background1)
        for x in range(0, size[0]):
            for y in range(0, size[1]):
                if (x + y) % 2 == 0:
                    img.putpixel((x, y), background2)
        return (img, ImageDraw.Draw(img))

    def test_square(self):
        expected = Image.open(os.path.join(IMAGES_PATH, 'square.png'))
        expected.load()
        img, draw = self.create_base_image_draw((10, 10))
        draw.polygon([(2, 2), (2, 7), (7, 7), (7, 2)], BLACK)
        self.assert_image_equal(img, expected,
                                'square as normal polygon failed')
        img, draw = self.create_base_image_draw((10, 10))
        draw.polygon([(7, 7), (7, 2), (2, 2), (2, 7)], BLACK)
        self.assert_image_equal(img, expected,
                                'square as inverted polygon failed')
        img, draw = self.create_base_image_draw((10, 10))
        draw.rectangle((2, 2, 7, 7), BLACK)
        self.assert_image_equal(img, expected,
                                'square as normal rectangle failed')
        img, draw = self.create_base_image_draw((10, 10))
        draw.rectangle((7, 7, 2, 2), BLACK)
        self.assert_image_equal(
            img, expected, 'square as inverted rectangle failed')

    def test_triangle_right(self):
        expected = Image.open(os.path.join(IMAGES_PATH, 'triangle_right.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.polygon([(3, 5), (17, 5), (10, 12)], BLACK)
        self.assert_image_equal(img, expected, 'triangle right failed')

    def test_line_horizontal(self):
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_horizontal_w2px_normal.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 5), BLACK, 2)
        self.assert_image_equal(
            img, expected, 'line straight horizontal normal 2px wide failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_horizontal_w2px_inverted.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((14, 5, 5, 5), BLACK, 2)
        self.assert_image_equal(
            img, expected, 'line straight horizontal inverted 2px wide failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_horizontal_w3px.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 5), BLACK, 3)
        self.assert_image_equal(
            img, expected, 'line straight horizontal normal 3px wide failed')
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((14, 5, 5, 5), BLACK, 3)
        self.assert_image_equal(
            img, expected, 'line straight horizontal inverted 3px wide failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_horizontal_w101px.png'))
        expected.load()
        img, draw = self.create_base_image_draw((200, 110))
        draw.line((5, 55, 195, 55), BLACK, 101)
        self.assert_image_equal(
            img, expected, 'line straight horizontal 101px wide failed')

    def test_line_h_s1_w2(self):
        self.skipTest('failing')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_horizontal_slope1px_w2px.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 6), BLACK, 2)
        self.assert_image_equal(
            img, expected, 'line horizontal 1px slope 2px wide failed')

    def test_line_vertical(self):
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_vertical_w2px_normal.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 5, 5, 14), BLACK, 2)
        self.assert_image_equal(
            img, expected, 'line straight vertical normal 2px wide failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_vertical_w2px_inverted.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 14, 5, 5), BLACK, 2)
        self.assert_image_equal(
            img, expected, 'line straight vertical inverted 2px wide failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_vertical_w3px.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 5, 5, 14), BLACK, 3)
        self.assert_image_equal(
            img, expected, 'line straight vertical normal 3px wide failed')
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 14, 5, 5), BLACK, 3)
        self.assert_image_equal(
            img, expected, 'line straight vertical inverted 3px wide failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_vertical_w101px.png'))
        expected.load()
        img, draw = self.create_base_image_draw((110, 200))
        draw.line((55, 5, 55, 195), BLACK, 101)
        self.assert_image_equal(img, expected,
                                'line straight vertical 101px wide failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_vertical_slope1px_w2px.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 5, 6, 14), BLACK, 2)
        self.assert_image_equal(img, expected,
                                'line vertical 1px slope 2px wide failed')

    def test_line_oblique_45(self):
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_oblique_45_w3px_a.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 14), BLACK, 3)
        self.assert_image_equal(img, expected,
                                'line oblique 45 normal 3px wide A failed')
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((14, 14, 5, 5), BLACK, 3)
        self.assert_image_equal(img, expected,
                                'line oblique 45 inverted 3px wide A failed')
        expected = Image.open(os.path.join(IMAGES_PATH,
                              'line_oblique_45_w3px_b.png'))
        expected.load()
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((14, 5, 5, 14), BLACK, 3)
        self.assert_image_equal(img, expected,
                                'line oblique 45 normal 3px wide B failed')
        img, draw = self.create_base_image_draw((20, 20))
        draw.line((5, 14, 14, 5), BLACK, 3)
        self.assert_image_equal(img, expected,
                                'line oblique 45 inverted 3px wide B failed')

    def test_wide_line_dot(self):
        # Test drawing a wide "line" from one point to another just draws
        # a single point
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)
        expected = "Tests/images/imagedraw_wide_line_dot.png"

        # Act
        draw.line([(50, 50), (50, 50)], width=3)

        # Assert
        self.assert_image_similar(im, Image.open(expected), 1)


if __name__ == '__main__':
    unittest.main()
