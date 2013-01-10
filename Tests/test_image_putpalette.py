from tester import *

from PIL import Image
from PIL import ImagePalette

def test_putpalette():
    def palette(mode):
        im = lena(mode).copy()
        im.putpalette(list(range(256))*3)
        p = im.getpalette()
        if p:
            return im.mode, p[:10]
        return im.mode
    assert_exception(ValueError, lambda: palette("1"))
    assert_equal(palette("L"), ("P", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    assert_equal(palette("P"), ("P", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
    assert_exception(ValueError, lambda: palette("I"))
    assert_exception(ValueError, lambda: palette("F"))
    assert_exception(ValueError, lambda: palette("RGB"))
    assert_exception(ValueError, lambda: palette("RGBA"))
    assert_exception(ValueError, lambda: palette("YCbCr"))

def test_imagepalette():
    im = lena("P")
    assert_no_exception(lambda: im.putpalette(ImagePalette.negative()))
    assert_no_exception(lambda: im.putpalette(ImagePalette.random()))
    assert_no_exception(lambda: im.putpalette(ImagePalette.sepia()))
    assert_no_exception(lambda: im.putpalette(ImagePalette.wedge()))
