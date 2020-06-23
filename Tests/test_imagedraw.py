import os.path

import pytest
from PIL import Image, ImageColor, ImageDraw, ImageFont

from .helper import (
    assert_image_equal,
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


def test_sanity():
    im = hopper("RGB").copy()

    draw = ImageDraw.ImageDraw(im)
    draw = ImageDraw.Draw(im)

    draw.ellipse(list(range(4)))
    draw.line(list(range(10)))
    draw.polygon(list(range(100)))
    draw.rectangle(list(range(4)))


def test_valueerror():
    with Image.open("Tests/images/chi.gif") as im:

        draw = ImageDraw.Draw(im)
        draw.line((0, 0), fill=(0, 0, 0))


def test_mode_mismatch():
    im = hopper("RGB").copy()

    with pytest.raises(ValueError):
        ImageDraw.ImageDraw(im, mode="L")


def helper_arc(bbox, start, end):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(bbox, start, end)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc.png", 1)


def test_arc1():
    helper_arc(BBOX1, 0, 180)
    helper_arc(BBOX1, 0.5, 180.4)


def test_arc2():
    helper_arc(BBOX2, 0, 180)
    helper_arc(BBOX2, 0.5, 180.4)


def test_arc_end_le_start():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    start = 270.5
    end = 0

    # Act
    draw.arc(BBOX1, start=start, end=end)

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_arc_end_le_start.png"))


def test_arc_no_loops():
    # No need to go in loops
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    start = 5
    end = 370

    # Act
    draw.arc(BBOX1, start=start, end=end)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_no_loops.png", 1)


def test_arc_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(BBOX1, 10, 260, width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_width.png", 1)


def test_arc_width_pieslice_large():
    # Tests an arc with a large enough width that it is a pieslice
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(BBOX1, 10, 260, fill="yellow", width=100)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_width_pieslice.png", 1)


def test_arc_width_fill():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.arc(BBOX1, 10, 260, fill="yellow", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_arc_width_fill.png", 1)


def test_arc_width_non_whole_angle():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_arc_width_non_whole_angle.png"

    # Act
    draw.arc(BBOX1, 10, 259.5, width=5)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


def test_bitmap():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    with Image.open("Tests/images/pil123rgba.png") as small:
        small = small.resize((50, 50), Image.NEAREST)

        # Act
        draw.bitmap((10, 10), small)

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_bitmap.png"))


def helper_chord(mode, bbox, start, end):
    # Arrange
    im = Image.new(mode, (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_chord_{}.png".format(mode)

    # Act
    draw.chord(bbox, start, end, fill="red", outline="yellow")

    # Assert
    assert_image_similar_tofile(im, expected, 1)


def test_chord1():
    for mode in ["RGB", "L"]:
        helper_chord(mode, BBOX1, 0, 180)
        helper_chord(mode, BBOX1, 0.5, 180.4)


def test_chord2():
    for mode in ["RGB", "L"]:
        helper_chord(mode, BBOX2, 0, 180)
        helper_chord(mode, BBOX2, 0.5, 180.4)


def test_chord_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(BBOX1, 10, 260, outline="yellow", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_chord_width.png", 1)


def test_chord_width_fill():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(BBOX1, 10, 260, fill="red", outline="yellow", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_chord_width_fill.png", 1)


def test_chord_zero_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(BBOX1, 10, 260, fill="red", outline="yellow", width=0)

    # Assert
    with Image.open("Tests/images/imagedraw_chord_zero_width.png") as expected:
        assert_image_equal(im, expected)


def helper_ellipse(mode, bbox):
    # Arrange
    im = Image.new(mode, (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_ellipse_{}.png".format(mode)

    # Act
    draw.ellipse(bbox, fill="green", outline="blue")

    # Assert
    assert_image_similar_tofile(im, expected, 1)


def test_ellipse1():
    for mode in ["RGB", "L"]:
        helper_ellipse(mode, BBOX1)


def test_ellipse2():
    for mode in ["RGB", "L"]:
        helper_ellipse(mode, BBOX2)


def test_ellipse_translucent():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im, "RGBA")

    # Act
    draw.ellipse(BBOX1, fill=(0, 255, 0, 127))

    # Assert
    expected = "Tests/images/imagedraw_ellipse_translucent.png"
    assert_image_similar_tofile(im, expected, 1)


def test_ellipse_edge():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(((0, 0), (W - 1, H)), fill="white")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_edge.png", 1)


def test_ellipse_symmetric():
    for bbox in [(25, 25, 76, 76), (25, 25, 75, 75)]:
        im = Image.new("RGB", (101, 101))
        draw = ImageDraw.Draw(im)
        draw.ellipse(bbox, fill="green", outline="blue")
        assert_image_equal(im, im.transpose(Image.FLIP_LEFT_RIGHT))


def test_ellipse_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(BBOX1, outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_width.png", 1)


def test_ellipse_width_large():
    # Arrange
    im = Image.new("RGB", (500, 500))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse((25, 25, 475, 475), outline="blue", width=75)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_width_large.png", 1)


def test_ellipse_width_fill():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(BBOX1, fill="green", outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_ellipse_width_fill.png", 1)


def test_ellipse_zero_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(BBOX1, fill="green", outline="blue", width=0)

    # Assert
    with Image.open("Tests/images/imagedraw_ellipse_zero_width.png") as expected:
        assert_image_equal(im, expected)


def helper_line(points):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.line(points, fill="yellow", width=2)

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_line.png"))


def test_line1():
    helper_line(POINTS1)


def test_line2():
    helper_line(POINTS2)


def test_shape1():
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
    assert_image_equal(im, Image.open("Tests/images/imagedraw_shape1.png"))


def test_shape2():
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
    assert_image_equal(im, Image.open("Tests/images/imagedraw_shape2.png"))


def helper_pieslice(bbox, start, end):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(bbox, start, end, fill="white", outline="blue")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_pieslice.png", 1)


def test_pieslice1():
    helper_pieslice(BBOX1, -90, 45)
    helper_pieslice(BBOX1, -90.5, 45.4)


def test_pieslice2():
    helper_pieslice(BBOX2, -90, 45)
    helper_pieslice(BBOX2, -90.5, 45.4)


def test_pieslice_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(BBOX1, 10, 260, outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_pieslice_width.png", 1)


def test_pieslice_width_fill():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_pieslice_width_fill.png"

    # Act
    draw.pieslice(BBOX1, 10, 260, fill="white", outline="blue", width=5)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


def test_pieslice_zero_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(BBOX1, 10, 260, fill="white", outline="blue", width=0)

    # Assert
    with Image.open("Tests/images/imagedraw_pieslice_zero_width.png") as expected:
        assert_image_equal(im, expected)


def helper_point(points):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.point(points, fill="yellow")

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_point.png"))


def test_point1():
    helper_point(POINTS1)


def test_point2():
    helper_point(POINTS2)


def helper_polygon(points):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.polygon(points, fill="red", outline="blue")

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_polygon.png"))


def test_polygon1():
    helper_polygon(POINTS1)


def test_polygon2():
    helper_polygon(POINTS2)


def test_polygon_kite():
    # Test drawing lines of different gradients (dx>dy, dy>dx) and
    # vertical (dx==0) and horizontal (dy==0) lines
    for mode in ["RGB", "L"]:
        # Arrange
        im = Image.new(mode, (W, H))
        draw = ImageDraw.Draw(im)
        expected = "Tests/images/imagedraw_polygon_kite_{}.png".format(mode)

        # Act
        draw.polygon(KITE_POINTS, fill="blue", outline="yellow")

        # Assert
        assert_image_equal(im, Image.open(expected))


def test_polygon_1px_high():
    # Test drawing a 1px high polygon
    # Arrange
    im = Image.new("RGB", (3, 3))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_polygon_1px_high.png"

    # Act
    draw.polygon([(0, 1), (0, 1), (2, 1), (2, 1)], "#f00")

    # Assert
    assert_image_equal(im, Image.open(expected))


def helper_rectangle(bbox):
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(bbox, fill="black", outline="green")

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_rectangle.png"))


def test_rectangle1():
    helper_rectangle(BBOX1)


def test_rectangle2():
    helper_rectangle(BBOX2)


def test_big_rectangle():
    # Test drawing a rectangle bigger than the image
    # Arrange
    im = Image.new("RGB", (W, H))
    bbox = [(-1, -1), (W + 1, H + 1)]
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(bbox, fill="orange")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_big_rectangle.png", 1)


def test_rectangle_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_rectangle_width.png"

    # Act
    draw.rectangle(BBOX1, outline="green", width=5)

    # Assert
    assert_image_equal(im, Image.open(expected))


def test_rectangle_width_fill():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_rectangle_width_fill.png"

    # Act
    draw.rectangle(BBOX1, fill="blue", outline="green", width=5)

    # Assert
    assert_image_equal(im, Image.open(expected))


def test_rectangle_zero_width():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(BBOX1, fill="blue", outline="green", width=0)

    # Assert
    with Image.open("Tests/images/imagedraw_rectangle_zero_width.png") as expected:
        assert_image_equal(im, expected)


def test_rectangle_I16():
    # Arrange
    im = Image.new("I;16", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(BBOX1, fill="black", outline="green")

    # Assert
    assert_image_equal(
        im.convert("I"), Image.open("Tests/images/imagedraw_rectangle_I.png")
    )


def test_floodfill():
    red = ImageColor.getrgb("red")

    for mode, value in [("L", 1), ("RGBA", (255, 0, 0, 0)), ("RGB", red)]:
        # Arrange
        im = Image.new(mode, (W, H))
        draw = ImageDraw.Draw(im)
        draw.rectangle(BBOX2, outline="yellow", fill="green")
        centre_point = (int(W / 2), int(H / 2))

        # Act
        ImageDraw.floodfill(im, centre_point, value)

        # Assert
        expected = "Tests/images/imagedraw_floodfill_" + mode + ".png"
        with Image.open(expected) as im_floodfill:
            assert_image_equal(im, im_floodfill)

    # Test that using the same colour does not change the image
    ImageDraw.floodfill(im, centre_point, red)
    assert_image_equal(im, im_floodfill)

    # Test that filling outside the image does not change the image
    ImageDraw.floodfill(im, (W, H), red)
    assert_image_equal(im, im_floodfill)

    # Test filling at the edge of an image
    im = Image.new("RGB", (1, 1))
    ImageDraw.floodfill(im, (0, 0), red)
    assert_image_equal(im, Image.new("RGB", (1, 1), red))


def test_floodfill_border():
    # floodfill() is experimental

    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    draw.rectangle(BBOX2, outline="yellow", fill="green")
    centre_point = (int(W / 2), int(H / 2))

    # Act
    ImageDraw.floodfill(
        im, centre_point, ImageColor.getrgb("red"), border=ImageColor.getrgb("black"),
    )

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_floodfill2.png"))


def test_floodfill_thresh():
    # floodfill() is experimental

    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    draw.rectangle(BBOX2, outline="darkgreen", fill="green")
    centre_point = (int(W / 2), int(H / 2))

    # Act
    ImageDraw.floodfill(im, centre_point, ImageColor.getrgb("red"), thresh=30)

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_floodfill2.png"))


def test_floodfill_not_negative():
    # floodfill() is experimental
    # Test that floodfill does not extend into negative coordinates

    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    draw.line((W / 2, 0, W / 2, H / 2), fill="green")
    draw.line((0, H / 2, W / 2, H / 2), fill="green")

    # Act
    ImageDraw.floodfill(im, (int(W / 4), int(H / 4)), ImageColor.getrgb("red"))

    # Assert
    assert_image_equal(
        im, Image.open("Tests/images/imagedraw_floodfill_not_negative.png")
    )


def create_base_image_draw(
    size, mode=DEFAULT_MODE, background1=WHITE, background2=GRAY
):
    img = Image.new(mode, size, background1)
    for x in range(0, size[0]):
        for y in range(0, size[1]):
            if (x + y) % 2 == 0:
                img.putpixel((x, y), background2)
    return img, ImageDraw.Draw(img)


def test_square():
    with Image.open(os.path.join(IMAGES_PATH, "square.png")) as expected:
        expected.load()
        img, draw = create_base_image_draw((10, 10))
        draw.polygon([(2, 2), (2, 7), (7, 7), (7, 2)], BLACK)
        assert_image_equal(img, expected, "square as normal polygon failed")
        img, draw = create_base_image_draw((10, 10))
        draw.polygon([(7, 7), (7, 2), (2, 2), (2, 7)], BLACK)
        assert_image_equal(img, expected, "square as inverted polygon failed")
        img, draw = create_base_image_draw((10, 10))
        draw.rectangle((2, 2, 7, 7), BLACK)
        assert_image_equal(img, expected, "square as normal rectangle failed")
        img, draw = create_base_image_draw((10, 10))
        draw.rectangle((7, 7, 2, 2), BLACK)
        assert_image_equal(img, expected, "square as inverted rectangle failed")


def test_triangle_right():
    with Image.open(os.path.join(IMAGES_PATH, "triangle_right.png")) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.polygon([(3, 5), (17, 5), (10, 12)], BLACK)
        assert_image_equal(img, expected, "triangle right failed")


def test_line_horizontal():
    with Image.open(
        os.path.join(IMAGES_PATH, "line_horizontal_w2px_normal.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 5), BLACK, 2)
        assert_image_equal(
            img, expected, "line straight horizontal normal 2px wide failed"
        )
    with Image.open(
        os.path.join(IMAGES_PATH, "line_horizontal_w2px_inverted.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((14, 5, 5, 5), BLACK, 2)
        assert_image_equal(
            img, expected, "line straight horizontal inverted 2px wide failed"
        )
    with Image.open(os.path.join(IMAGES_PATH, "line_horizontal_w3px.png")) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 5), BLACK, 3)
        assert_image_equal(
            img, expected, "line straight horizontal normal 3px wide failed"
        )
        img, draw = create_base_image_draw((20, 20))
        draw.line((14, 5, 5, 5), BLACK, 3)
        assert_image_equal(
            img, expected, "line straight horizontal inverted 3px wide failed"
        )
    with Image.open(
        os.path.join(IMAGES_PATH, "line_horizontal_w101px.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((200, 110))
        draw.line((5, 55, 195, 55), BLACK, 101)
        assert_image_equal(img, expected, "line straight horizontal 101px wide failed")


def test_line_h_s1_w2():
    pytest.skip("failing")
    with Image.open(
        os.path.join(IMAGES_PATH, "line_horizontal_slope1px_w2px.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 6), BLACK, 2)
        assert_image_equal(img, expected, "line horizontal 1px slope 2px wide failed")


def test_line_vertical():
    with Image.open(
        os.path.join(IMAGES_PATH, "line_vertical_w2px_normal.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 5, 5, 14), BLACK, 2)
        assert_image_equal(
            img, expected, "line straight vertical normal 2px wide failed"
        )
    with Image.open(
        os.path.join(IMAGES_PATH, "line_vertical_w2px_inverted.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 14, 5, 5), BLACK, 2)
        assert_image_equal(
            img, expected, "line straight vertical inverted 2px wide failed"
        )
    with Image.open(os.path.join(IMAGES_PATH, "line_vertical_w3px.png")) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 5, 5, 14), BLACK, 3)
        assert_image_equal(
            img, expected, "line straight vertical normal 3px wide failed"
        )
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 14, 5, 5), BLACK, 3)
        assert_image_equal(
            img, expected, "line straight vertical inverted 3px wide failed"
        )
    with Image.open(os.path.join(IMAGES_PATH, "line_vertical_w101px.png")) as expected:
        expected.load()
        img, draw = create_base_image_draw((110, 200))
        draw.line((55, 5, 55, 195), BLACK, 101)
        assert_image_equal(img, expected, "line straight vertical 101px wide failed")
    with Image.open(
        os.path.join(IMAGES_PATH, "line_vertical_slope1px_w2px.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 5, 6, 14), BLACK, 2)
        assert_image_equal(img, expected, "line vertical 1px slope 2px wide failed")


def test_line_oblique_45():
    with Image.open(
        os.path.join(IMAGES_PATH, "line_oblique_45_w3px_a.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 5, 14, 14), BLACK, 3)
        assert_image_equal(img, expected, "line oblique 45 normal 3px wide A failed")
        img, draw = create_base_image_draw((20, 20))
        draw.line((14, 14, 5, 5), BLACK, 3)
        assert_image_equal(img, expected, "line oblique 45 inverted 3px wide A failed")
    with Image.open(
        os.path.join(IMAGES_PATH, "line_oblique_45_w3px_b.png")
    ) as expected:
        expected.load()
        img, draw = create_base_image_draw((20, 20))
        draw.line((14, 5, 5, 14), BLACK, 3)
        assert_image_equal(img, expected, "line oblique 45 normal 3px wide B failed")
        img, draw = create_base_image_draw((20, 20))
        draw.line((5, 14, 14, 5), BLACK, 3)
        assert_image_equal(img, expected, "line oblique 45 inverted 3px wide B failed")


def test_wide_line_dot():
    # Test drawing a wide "line" from one point to another just draws a single point
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    draw.line([(50, 50), (50, 50)], width=3)

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_wide_line_dot.png", 1)


def test_wide_line_larger_than_int():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    expected = "Tests/images/imagedraw_wide_line_larger_than_int.png"

    # Act
    draw.line([(0, 0), (32768, 32768)], width=3)

    # Assert
    assert_image_similar_tofile(im, expected, 1)


@pytest.mark.parametrize(
    "xy",
    [
        [
            (400, 280),
            (380, 280),
            (450, 280),
            (440, 120),
            (350, 200),
            (310, 280),
            (300, 280),
            (250, 280),
            (250, 200),
            (150, 200),
            (150, 260),
            (50, 200),
            (150, 50),
            (250, 100),
        ],
        (
            400,
            280,
            380,
            280,
            450,
            280,
            440,
            120,
            350,
            200,
            310,
            280,
            300,
            280,
            250,
            280,
            250,
            200,
            150,
            200,
            150,
            260,
            50,
            200,
            150,
            50,
            250,
            100,
        ),
        [
            400,
            280,
            380,
            280,
            450,
            280,
            440,
            120,
            350,
            200,
            310,
            280,
            300,
            280,
            250,
            280,
            250,
            200,
            150,
            200,
            150,
            260,
            50,
            200,
            150,
            50,
            250,
            100,
        ],
    ],
)
def test_line_joint(xy):
    im = Image.new("RGB", (500, 325))
    draw = ImageDraw.Draw(im)

    # Act
    draw.line(xy, GRAY, 50, "curve")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_line_joint_curve.png", 3)


def test_textsize_empty_string():
    # https://github.com/python-pillow/Pillow/issues/2783
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)

    # Act
    # Should not cause 'SystemError: <built-in method getsize of
    # ImagingFont object at 0x...> returned NULL without setting an error'
    draw.textsize("")
    draw.textsize("\n")
    draw.textsize("test\n")


@skip_unless_feature("freetype2")
def test_textsize_stroke():
    # Arrange
    im = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 20)

    # Act / Assert
    assert draw.textsize("A", font, stroke_width=2) == (16, 20)
    assert draw.multiline_textsize("ABC\nAaaa", font, stroke_width=2) == (52, 44)


@skip_unless_feature("freetype2")
def test_stroke():
    for suffix, stroke_fill in {"same": None, "different": "#0f0"}.items():
        # Arrange
        im = Image.new("RGB", (120, 130))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

        # Act
        draw.text((10, 10), "A", "#f00", font, stroke_width=2, stroke_fill=stroke_fill)

        # Assert
        assert_image_similar_tofile(
            im, "Tests/images/imagedraw_stroke_" + suffix + ".png", 3.1
        )


@skip_unless_feature("freetype2")
def test_stroke_descender():
    # Arrange
    im = Image.new("RGB", (120, 130))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    # Act
    draw.text((10, 0), "y", "#f00", font, stroke_width=2, stroke_fill="#0f0")

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_stroke_descender.png", 6.76)


@skip_unless_feature("freetype2")
def test_stroke_multiline():
    # Arrange
    im = Image.new("RGB", (100, 250))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 120)

    # Act
    draw.multiline_text(
        (10, 10), "A\nB", "#f00", font, stroke_width=2, stroke_fill="#0f0"
    )

    # Assert
    assert_image_similar_tofile(im, "Tests/images/imagedraw_stroke_multiline.png", 3.3)


def test_same_color_outline():
    # Prepare shape
    x0, y0 = 5, 5
    x1, y1 = 5, 50
    x2, y2 = 95, 50
    x3, y3 = 95, 5

    s = ImageDraw.Outline()
    s.move(x0, y0)
    s.curve(x1, y1, x2, y2, x3, y3)
    s.line(x0, y0)

    # Begin
    for mode in ["RGB", "L"]:
        for fill, outline in [["red", None], ["red", "red"], ["red", "#f00"]]:
            for operation, args in {
                "chord": [BBOX1, 0, 180],
                "ellipse": [BBOX1],
                "shape": [s],
                "pieslice": [BBOX1, -90, 45],
                "polygon": [[(18, 30), (85, 30), (60, 72)]],
                "rectangle": [BBOX1],
            }.items():
                # Arrange
                im = Image.new(mode, (W, H))
                draw = ImageDraw.Draw(im)

                # Act
                draw_method = getattr(draw, operation)
                args += [fill, outline]
                draw_method(*args)

                # Assert
                expected = "Tests/images/imagedraw_outline_{}_{}.png".format(
                    operation, mode
                )
                assert_image_similar_tofile(im, expected, 1)
