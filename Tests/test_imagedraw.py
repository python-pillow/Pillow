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


class TestImageDraw(PillowTestCase):

    def test_sanity(self):
        im = hopper("RGB").copy()

        draw = ImageDraw.ImageDraw(im)
        draw = ImageDraw.Draw(im)

        draw.ellipse(list(range(4)))
        draw.line(list(range(10)))
        draw.polygon(list(range(100)))
        draw.rectangle(list(range(4)))

    def test_removed_methods(self):
        im = hopper()

        draw = ImageDraw.Draw(im)

        self.assertRaises(Exception, lambda: draw.setink(0))
        self.assertRaises(Exception, lambda: draw.setfill(0))

    def test_mode_mismatch(self):
        im = hopper("RGB").copy()

        self.assertRaises(ValueError,
                          lambda: ImageDraw.ImageDraw(im, mode="L"))

    def helper_arc(self, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        # FIXME Fill param should be named outline.
        draw.arc(bbox, 0, 180)
        del draw

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_arc.png"), 1)

    def test_arc1(self):
        self.helper_arc(BBOX1)

    def test_arc2(self):
        self.helper_arc(BBOX2)

    def test_bitmap(self):
        # Arrange
        small = Image.open("Tests/images/pil123rgba.png").resize((50, 50))
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.bitmap((10, 10), small)
        del draw

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_bitmap.png"))

    def helper_chord(self, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.chord(bbox, 0, 180, fill="red", outline="yellow")
        del draw

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_chord.png"), 1)

    def test_chord1(self):
        self.helper_chord(BBOX1)

    def test_chord2(self):
        self.helper_chord(BBOX2)

    def helper_ellipse(self, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.ellipse(bbox, fill="green", outline="blue")
        del draw

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_ellipse.png"), 1)

    def test_ellipse1(self):
        self.helper_ellipse(BBOX1)

    def test_ellipse2(self):
        self.helper_ellipse(BBOX2)

    def test_ellipse_edge(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.ellipse(((0, 0), (W-1, H)), fill="white")
        del draw

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_ellipse_edge.png"), 1)

    def helper_line(self, points):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.line(points, fill="yellow", width=2)
        del draw

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_line.png"))

    def test_line1(self):
        self.helper_line(POINTS1)

    def test_line2(self):
        self.helper_line(POINTS2)

    def helper_pieslice(self, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.pieslice(bbox, -90, 45, fill="white", outline="blue")
        del draw

        # Assert
        self.assert_image_similar(
            im, Image.open("Tests/images/imagedraw_pieslice.png"), 1)

    def test_pieslice1(self):
        self.helper_pieslice(BBOX1)

    def test_pieslice2(self):
        self.helper_pieslice(BBOX2)

    def helper_point(self, points):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.point(points, fill="yellow")
        del draw

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
        del draw

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_polygon.png"))

    def test_polygon1(self):
        self.helper_polygon(POINTS1)

    def test_polygon2(self):
        self.helper_polygon(POINTS2)

    def helper_rectangle(self, bbox):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)

        # Act
        draw.rectangle(bbox, fill="black", outline="green")
        del draw

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_rectangle.png"))

    def test_rectangle1(self):
        self.helper_rectangle(BBOX1)

    def test_rectangle2(self):
        self.helper_rectangle(BBOX2)

    def test_floodfill(self):
        # Arrange
        im = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(im)
        draw.rectangle(BBOX2, outline="yellow", fill="green")
        centre_point = (int(W/2), int(H/2))

        # Act
        ImageDraw.floodfill(im, centre_point, ImageColor.getrgb("red"))
        del draw

        # Assert
        self.assert_image_equal(
            im, Image.open("Tests/images/imagedraw_floodfill.png"))

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
        del draw

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


if __name__ == '__main__':
    unittest.main()

# End of file
