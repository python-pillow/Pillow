from tester import *

from PIL import Image

def test_sanity():

    im = lena()

    projection = im.getprojection()

    assert_equal(len(projection), 2)
    assert_equal(len(projection[0]), im.size[0])
    assert_equal(len(projection[1]), im.size[1])

    # 8-bit image
    im = Image.new("L", (10, 10))
    assert_equal(im.getprojection()[0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    assert_equal(im.getprojection()[1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    im.paste(255, (2, 4, 8, 6))
    assert_equal(im.getprojection()[0], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0])
    assert_equal(im.getprojection()[1], [0, 0, 0, 0, 1, 1, 0, 0, 0, 0])

    # 32-bit image
    im = Image.new("RGB", (10, 10))
    assert_equal(im.getprojection()[0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    assert_equal(im.getprojection()[1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    im.paste(255, (2, 4, 8, 6))
    assert_equal(im.getprojection()[0], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0])
    assert_equal(im.getprojection()[1], [0, 0, 0, 0, 1, 1, 0, 0, 0, 0])

