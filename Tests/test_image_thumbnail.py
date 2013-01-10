from tester import *

from PIL import Image

def test_sanity():

    im = lena()
    im.thumbnail((100, 100))

    assert_image(im, im.mode, (100, 100))

def test_aspect():

    im = lena()
    im.thumbnail((100, 100))
    assert_image(im, im.mode, (100, 100))

    im = lena().resize((128, 256))
    im.thumbnail((100, 100))
    assert_image(im, im.mode, (50, 100))

    im = lena().resize((128, 256))
    im.thumbnail((50, 100))
    assert_image(im, im.mode, (50, 100))

    im = lena().resize((256, 128))
    im.thumbnail((100, 100))
    assert_image(im, im.mode, (100, 50))

    im = lena().resize((256, 128))
    im.thumbnail((100, 50))
    assert_image(im, im.mode, (100, 50))

    im = lena().resize((128, 128))
    im.thumbnail((100, 100))
    assert_image(im, im.mode, (100, 100))
