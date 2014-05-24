from tester import *

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw

# Image size
w, h = 100, 100

# Bounding box points
x0 = int(w / 4)
x1 = int(x0 * 3)
y0 = int(h / 4)
y1 = int(x0 * 3)

# Two kinds of bounding box
bbox1 = [(x0, y0), (x1, y1)]
bbox2 = [x0, y0, x1, y1]

# Two kinds of coordinate sequences
points1 = [(10, 10), (20, 40), (30, 30)]
points2 = [10, 10, 20, 40, 30, 30]


def test_sanity():

    im = lena("RGB").copy()

    draw = ImageDraw.ImageDraw(im)
    draw = ImageDraw.Draw(im)

    draw.ellipse(list(range(4)))
    draw.line(list(range(10)))
    draw.polygon(list(range(100)))
    draw.rectangle(list(range(4)))

    success()


def test_deprecated():

    im = lena().copy()

    draw = ImageDraw.Draw(im)

    assert_warning(DeprecationWarning, lambda: draw.setink(0))
    assert_warning(DeprecationWarning, lambda: draw.setfill(0))


def helper_arc(bbox):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    # FIXME Fill param should be named outline.
    draw.arc(bbox, 0, 180)
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_arc.png"))


def test_arc1():
     assert_exception(TypeError, lambda: helper_arc(bbox1))


def test_arc2():
    helper_arc(bbox2)


def test_bitmap():
    # Arrange
    small = Image.open("Tests/images/pil123rgba.png").resize((50, 50))
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.bitmap((10, 10), small)
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_bitmap.png"))


def helper_chord(bbox):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(bbox, 0, 180, fill="red", outline="yellow")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_chord.png"))


def test_chord1():
     assert_exception(TypeError, lambda: helper_chord(bbox1))


def test_chord2():
    helper_chord(bbox2)


def helper_ellipse(bbox):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.ellipse(bbox, fill="green", outline="blue")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_ellipse.png"))


def test_ellipse1():
    helper_ellipse(bbox1)


def test_ellipse2():
    helper_ellipse(bbox2)


def helper_line(points):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.line(points1, fill="yellow", width=2)
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_line.png"))


def test_line1():
    helper_line(points1)


def test_line2():
    helper_line(points2)


def helper_pieslice(bbox):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(bbox, -90, 45, fill="white", outline="blue")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_pieslice.png"))


def test_pieslice1():
     assert_exception(TypeError, lambda: helper_pieslice(bbox1))


def test_pieslice2():
    helper_pieslice(bbox2)


def helper_point(points):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.point(points1, fill="yellow")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_point.png"))


def test_point1():
    helper_point(points1)


def test_point2():
    helper_point(points2)


def helper_polygon(points):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.polygon(points1, fill="red", outline="blue")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_polygon.png"))


def test_polygon1():
    helper_polygon(points1)


def test_polygon2():
    helper_polygon(points2)


def helper_rectangle(bbox):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.rectangle(bbox, fill="black", outline="green")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_rectangle.png"))


def test_rectangle1():
    helper_rectangle(bbox1)


def test_rectangle2():
    helper_rectangle(bbox2)


def test_floodfill():
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)
    draw.rectangle(bbox2, outline="yellow", fill="green")
    centre_point = (int(w/2), int(h/2))

    # Act
    ImageDraw.floodfill(im, centre_point, ImageColor.getrgb("red"))
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_floodfill.png"))


def test_floodfill_border():
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)
    draw.rectangle(bbox2, outline="yellow", fill="green")
    centre_point = (int(w/2), int(h/2))

    # Act
    ImageDraw.floodfill(
        im, centre_point, ImageColor.getrgb("red"),
        border=ImageColor.getrgb("black"))
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_floodfill2.png"))


# End of file
