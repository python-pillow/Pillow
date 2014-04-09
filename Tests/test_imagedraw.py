from tester import *

from PIL import Image
from PIL import ImageDraw
import os.path

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
DEFAULT_MODE = 'RGB'
IMAGES_PATH = os.path.join('Tests', 'images', 'imagedraw')

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


def create_base_image_draw(size, mode=DEFAULT_MODE, background1=WHITE, background2=GRAY):
    img = Image.new(mode, size, background1)
    for x in range(0, size[0]):
        for y in range(0, size[1]):
            if (x + y) % 2 == 0:
                img.putpixel((x, y), background2)
    return (img, ImageDraw.Draw(img))


def test_square():
    expected = Image.open(os.path.join(IMAGES_PATH, 'square.png'))
    expected.load()
    img, draw = create_base_image_draw((10, 10))
    draw.polygon([(2, 2), (2, 7), (7, 7), (7, 2)], BLACK)
    assert_image_equal(img, expected, 'square as normal polygon failed')
    img, draw = create_base_image_draw((10, 10))
    draw.polygon([(7, 7), (7, 2), (2, 2), (2, 7)], BLACK)
    assert_image_equal(img, expected, 'square as inverted polygon failed')
    img, draw = create_base_image_draw((10, 10))
    draw.rectangle((2, 2, 7, 7), BLACK)
    assert_image_equal(img, expected, 'square as normal rectangle failed')
    img, draw = create_base_image_draw((10, 10))
    draw.rectangle((7, 7, 2, 2), BLACK)
    assert_image_equal(img, expected, 'square as inverted rectangle failed')


def test_triangle_right():
    expected = Image.open(os.path.join(IMAGES_PATH, 'triangle_right.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.polygon([(3, 5), (17, 5), (10, 12)], BLACK)
    assert_image_equal(img, expected, 'triangle right failed')


def test_line_horizontal():
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_horizontal_w2px_normal.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 5), BLACK, 2)
    assert_image_equal(img, expected, 'line straigth horizontal normal 2px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_horizontal_w2px_inverted.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 5, 5, 5), BLACK, 2)
    assert_image_equal(img, expected, 'line straigth horizontal inverted 2px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_horizontal_w3px.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 5), BLACK, 3)
    assert_image_equal(img, expected, 'line straigth horizontal normal 3px wide failed')
    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 5, 5, 5), BLACK, 3)
    assert_image_equal(img, expected, 'line straigth horizontal inverted 3px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_horizontal_w101px.png'))
    expected.load()
    img, draw = create_base_image_draw((200, 110))
    draw.line((5, 55, 195, 55), BLACK, 101)
    assert_image_equal(img, expected, 'line straigth horizontal 101px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_horizontal_slope1px_w2px.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 6), BLACK, 2)
    assert_image_equal(img, expected, 'line horizontal 1px slope 2px wide failed')


def test_line_vertical():
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_vertical_w2px_normal.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 5, 14), BLACK, 2)
    assert_image_equal(img, expected, 'line straigth vertical normal 2px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_vertical_w2px_inverted.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 14, 5, 5), BLACK, 2)
    assert_image_equal(img, expected, 'line straigth vertical inverted 2px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_vertical_w3px.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 5, 14), BLACK, 3)
    assert_image_equal(img, expected, 'line straigth vertical normal 3px wide failed')
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 14, 5, 5), BLACK, 3)
    assert_image_equal(img, expected, 'line straigth vertical inverted 3px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_vertical_w101px.png'))
    expected.load()
    img, draw = create_base_image_draw((110, 200))
    draw.line((55, 5, 55, 195), BLACK, 101)
    assert_image_equal(img, expected, 'line straigth vertical 101px wide failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_vertical_slope1px_w2px.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 6, 14), BLACK, 2)
    assert_image_equal(img, expected, 'line vertical 1px slope 2px wide failed')


def test_line_oblique_45():
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_oblique_45_w3px_a.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 5, 14, 14), BLACK, 3)
    assert_image_equal(img, expected, 'line oblique 45º normal 3px wide A failed')
    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 14, 5, 5), BLACK, 3)
    assert_image_equal(img, expected, 'line oblique 45º inverted 3px wide A failed')
    expected = Image.open(os.path.join(IMAGES_PATH, 'line_oblique_45_w3px_b.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.line((14, 5, 5, 14), BLACK, 3)
    assert_image_equal(img, expected, 'line oblique 45º normal 3px wide B failed')
    img, draw = create_base_image_draw((20, 20))
    draw.line((5, 14, 14, 5), BLACK, 3)
    assert_image_equal(img, expected, 'line oblique 45º inverted 3px wide B failed')
