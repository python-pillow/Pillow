from tester import *

from PIL import Image

def test_offset():

    im1 = lena()

    im2 = assert_warning(DeprecationWarning, lambda: im1.offset(10))
    assert_equal(im1.getpixel((0, 0)), im2.getpixel((10, 10)))

    im2 = assert_warning(DeprecationWarning, lambda: im1.offset(10, 20))
    assert_equal(im1.getpixel((0, 0)), im2.getpixel((10, 20)))

    im2 = assert_warning(DeprecationWarning, lambda: im1.offset(20, 20))
    assert_equal(im1.getpixel((0, 0)), im2.getpixel((20, 20)))
