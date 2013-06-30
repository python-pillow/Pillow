from tester import *

from PIL import Image

FLIP_LEFT_RIGHT = Image.FLIP_LEFT_RIGHT
FLIP_TOP_BOTTOM = Image.FLIP_TOP_BOTTOM
ROTATE_90 = Image.ROTATE_90
ROTATE_180 = Image.ROTATE_180
ROTATE_270 = Image.ROTATE_270

def test_sanity():

    im = lena()

    assert_no_exception(lambda: im.transpose(FLIP_LEFT_RIGHT))
    assert_no_exception(lambda: im.transpose(FLIP_TOP_BOTTOM))

    assert_no_exception(lambda: im.transpose(ROTATE_90))
    assert_no_exception(lambda: im.transpose(ROTATE_180))
    assert_no_exception(lambda: im.transpose(ROTATE_270))

def test_roundtrip():

    im = lena()

    def transpose(first, second):
        return im.transpose(first).transpose(second)

    assert_image_equal(im, transpose(FLIP_LEFT_RIGHT, FLIP_LEFT_RIGHT))
    assert_image_equal(im, transpose(FLIP_TOP_BOTTOM, FLIP_TOP_BOTTOM))

    assert_image_equal(im, transpose(ROTATE_90, ROTATE_270))
    assert_image_equal(im, transpose(ROTATE_180, ROTATE_180))

