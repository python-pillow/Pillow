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
    # Normal polygon
    img, draw = create_base_image_draw((10, 10))
    draw.polygon([(2, 2), (2, 7), (7, 7), (7, 2)], BLACK)
    assert_image_equal(img, expected)
    # Inverted polygon
    img, draw = create_base_image_draw((10, 10))
    draw.polygon([(7, 7), (7, 2), (2, 2), (2, 7)], BLACK)
    assert_image_equal(img, expected)
    # Normal rectangle
    img, draw = create_base_image_draw((10, 10))
    draw.rectangle((2, 2, 7, 7), BLACK)
    assert_image_equal(img, expected)
    # Inverted rectangle
    img, draw = create_base_image_draw((10, 10))
    draw.rectangle((7, 7, 2, 2), BLACK)
    assert_image_equal(img, expected)


def test_triangle_right():
    expected = Image.open(os.path.join(IMAGES_PATH, 'triangle_right.png'))
    expected.load()
    img, draw = create_base_image_draw((20, 20))
    draw.polygon([(3, 5), (17, 5), (10, 12)], BLACK)
    assert_image_equal(img, expected)
