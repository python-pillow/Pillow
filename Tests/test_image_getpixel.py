from tester import *

from PIL import Image

def color(mode):
    bands = Image.getmodebands(mode)
    if bands == 1:
        return 1
    else:
        return tuple(range(1, bands+1))

def test_pixel():
    
    def pixel(mode):
        c = color(mode)
        im = Image.new(mode, (1, 1), None)
        im.putpixel((0, 0), c)
        return im.getpixel((0, 0))

    assert_equal(pixel("1"), 1)
    assert_equal(pixel("L"), 1)
    assert_equal(pixel("LA"), (1, 2))
    assert_equal(pixel("I"), 1)
    assert_equal(pixel("I;16"), 1)
    assert_equal(pixel("I;16B"), 1)
    assert_equal(pixel("F"), 1.0)
    assert_equal(pixel("P"), 1)
    assert_equal(pixel("PA"), (1, 2))
    assert_equal(pixel("RGB"), (1, 2, 3))
    assert_equal(pixel("RGBA"), (1, 2, 3, 4))
    assert_equal(pixel("RGBX"), (1, 2, 3, 4))
    assert_equal(pixel("CMYK"), (1, 2, 3, 4))
    assert_equal(pixel("YCbCr"), (1, 2, 3))

def test_image():
    
    def pixel(mode):
        im = Image.new(mode, (1, 1), color(mode))
        return im.getpixel((0, 0))

    assert_equal(pixel("1"), 1)
    assert_equal(pixel("L"), 1)
    assert_equal(pixel("LA"), (1, 2))
    assert_equal(pixel("I"), 1)
    assert_equal(pixel("I;16"), 1)
    assert_equal(pixel("I;16B"), 1)
    assert_equal(pixel("F"), 1.0)
    assert_equal(pixel("P"), 1)
    assert_equal(pixel("PA"), (1, 2))
    assert_equal(pixel("RGB"), (1, 2, 3))
    assert_equal(pixel("RGBA"), (1, 2, 3, 4))
    assert_equal(pixel("RGBX"), (1, 2, 3, 4))
    assert_equal(pixel("CMYK"), (1, 2, 3, 4))
    assert_equal(pixel("YCbCr"), (1, 2, 3))


        
