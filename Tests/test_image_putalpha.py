from tester import *

from PIL import Image

def test_interface():

    im = Image.new("RGBA", (1, 1), (1, 2, 3, 0))
    assert_equal(im.getpixel((0, 0)), (1, 2, 3, 0))

    im = Image.new("RGBA", (1, 1), (1, 2, 3))
    assert_equal(im.getpixel((0, 0)), (1, 2, 3, 255))

    im.putalpha(Image.new("L", im.size, 4))
    assert_equal(im.getpixel((0, 0)), (1, 2, 3, 4))

    im.putalpha(5)
    assert_equal(im.getpixel((0, 0)), (1, 2, 3, 5))

def test_promote():

    im = Image.new("L", (1, 1), 1)
    assert_equal(im.getpixel((0, 0)), 1)

    im.putalpha(2)
    assert_equal(im.mode, 'LA')
    assert_equal(im.getpixel((0, 0)), (1, 2))

    im = Image.new("RGB", (1, 1), (1, 2, 3))
    assert_equal(im.getpixel((0, 0)), (1, 2, 3))

    im.putalpha(4)
    assert_equal(im.mode, 'RGBA')
    assert_equal(im.getpixel((0, 0)), (1, 2, 3, 4))

def test_readonly():

    im = Image.new("RGB", (1, 1), (1, 2, 3))
    im.readonly = 1

    im.putalpha(4)
    assert_false(im.readonly)
    assert_equal(im.mode, 'RGBA')
    assert_equal(im.getpixel((0, 0)), (1, 2, 3, 4))
