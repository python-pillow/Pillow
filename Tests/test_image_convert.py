from tester import *

from PIL import Image

def test_sanity():

    def convert(im, mode):
        out = im.convert(mode)
        assert_equal(out.mode, mode)
        assert_equal(out.size, im.size)

    modes = "1", "L", "I", "F", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr"

    for mode in modes:
        im = lena(mode)
        for mode in modes:
            yield_test(convert, im, mode)

def test_default():

    im = lena("P")
    assert_image(im, "P", im.size)
    im = im.convert()
    assert_image(im, "RGB", im.size)
    im = im.convert()
    assert_image(im, "RGB", im.size)
