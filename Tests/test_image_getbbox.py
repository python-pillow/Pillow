from tester import *

from PIL import Image

def test_sanity():

    bbox = lena().getbbox()
    assert_true(isinstance(bbox, tuple))

def test_bbox():

    # 8-bit mode
    im = Image.new("L", (100, 100), 0)
    assert_equal(im.getbbox(), None)

    im.paste(255, (10, 25, 90, 75))
    assert_equal(im.getbbox(), (10, 25, 90, 75))

    im.paste(255, (25, 10, 75, 90))
    assert_equal(im.getbbox(), (10, 10, 90, 90))

    im.paste(255, (-10, -10, 110, 110))
    assert_equal(im.getbbox(), (0, 0, 100, 100))

    # 32-bit mode
    im = Image.new("RGB", (100, 100), 0)
    assert_equal(im.getbbox(), None)

    im.paste(255, (10, 25, 90, 75))
    assert_equal(im.getbbox(), (10, 25, 90, 75))

    im.paste(255, (25, 10, 75, 90))
    assert_equal(im.getbbox(), (10, 10, 90, 90))

    im.paste(255, (-10, -10, 110, 110))
    assert_equal(im.getbbox(), (0, 0, 100, 100))
