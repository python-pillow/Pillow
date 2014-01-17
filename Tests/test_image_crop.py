from tester import *

from PIL import Image

def test_crop():
    def crop(mode):
        out = lena(mode).crop((50, 50, 100, 100))
        assert_equal(out.mode, mode)
        assert_equal(out.size, (50, 50))
    for mode in "1", "P", "L", "RGB", "I", "F":
        yield_test(crop, mode)

def test_wide_crop():

    def crop(*bbox):
        i = im.crop(bbox)
        h = i.histogram()
        while h and not h[-1]:
            del h[-1]
        return tuple(h)

    im = Image.new("L", (100, 100), 1)

    assert_equal(crop(0, 0, 100, 100), (0, 10000))
    assert_equal(crop(25, 25, 75, 75), (0, 2500))

    # sides
    assert_equal(crop(-25, 0, 25, 50), (1250, 1250))
    assert_equal(crop(0, -25, 50, 25), (1250, 1250))
    assert_equal(crop(75, 0, 125, 50), (1250, 1250))
    assert_equal(crop(0, 75, 50, 125), (1250, 1250))

    assert_equal(crop(-25, 25, 125, 75), (2500, 5000))
    assert_equal(crop(25, -25, 75, 125), (2500, 5000))

    # corners
    assert_equal(crop(-25, -25, 25, 25), (1875, 625))
    assert_equal(crop(75, -25, 125, 25), (1875, 625))
    assert_equal(crop(75, 75, 125, 125), (1875, 625))
    assert_equal(crop(-25, 75, 25, 125), (1875, 625))

# --------------------------------------------------------------------

def test_negative_crop():
    # Check negative crop size (@PIL171)

    im = Image.new("L", (512, 512))
    im = im.crop((400, 400, 200, 200))

    assert_equal(im.size, (0, 0))
    assert_equal(len(im.getdata()), 0)
    assert_exception(IndexError, lambda: im.getdata()[0])
