from tester import *

from PIL import Image
from PIL import ImageDraw

# Image size
w, h = 100, 100

# Bounding box points
x0 = w / 4
x1 = x0 * 3
y0 = h / 4
y1 = x0 * 3

# Two kinds of bounding box
bbox1 = [(x0, y0), (x1, y1)]
bbox2 = [x0, y0, x1, y1]


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
    # FIXME Should docs note 0 degrees is at 3 o'clock?
    # FIXME Fill param should be named outline.
    draw.arc(bbox, 0, 180)
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_arc.png"))


# FIXME
# def test_arc1():
#     helper_arc(bbox1)


def test_arc2():
    helper_arc(bbox2)


def helper_chord(bbox):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.chord(bbox, 0, 180, fill="red", outline="yellow")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_chord.png"))


# FIXME
# def test_chord1():
#     helper_chord(bbox1)


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


def helper_pieslice(bbox):
    # Arrange
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)

    # Act
    draw.pieslice(bbox, -90, 45, fill="white", outline="blue")
    del draw

    # Assert
    assert_image_equal(im, Image.open("Tests/images/imagedraw_pieslice.png"))


# FIXME
# def test_pieslice1():
#     helper_pieslice(bbox1)


def test_pieslice2():
    helper_pieslice(bbox2)


# End of file
