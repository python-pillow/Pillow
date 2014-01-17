from tester import *

import sys

from PIL import Image

def test_sanity():

    im1 = lena()

    data = list(im1.getdata())

    im2 = Image.new(im1.mode, im1.size, 0)
    im2.putdata(data)

    assert_image_equal(im1, im2)

    # readonly
    im2 = Image.new(im1.mode, im2.size, 0)
    im2.readonly = 1
    im2.putdata(data)

    assert_false(im2.readonly)
    assert_image_equal(im1, im2)


def test_long_integers():
    # see bug-200802-systemerror
    def put(value):
        im = Image.new("RGBA", (1, 1))
        im.putdata([value])
        return im.getpixel((0, 0))
    assert_equal(put(0xFFFFFFFF), (255, 255, 255, 255))
    assert_equal(put(0xFFFFFFFF), (255, 255, 255, 255))
    assert_equal(put(-1), (255, 255, 255, 255))
    assert_equal(put(-1), (255, 255, 255, 255))
    if sys.maxsize > 2**32:
        assert_equal(put(sys.maxsize), (255, 255, 255, 255))
    else:
        assert_equal(put(sys.maxsize), (255, 255, 255, 127))
