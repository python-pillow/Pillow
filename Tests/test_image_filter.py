from tester import *

from PIL import Image
from PIL import ImageFilter

def test_sanity():

    def filter(filter):
        im = lena("L")
        out = im.filter(filter)
        assert_equal(out.mode, im.mode)
        assert_equal(out.size, im.size)

    filter(ImageFilter.BLUR)
    filter(ImageFilter.CONTOUR)
    filter(ImageFilter.DETAIL)
    filter(ImageFilter.EDGE_ENHANCE)
    filter(ImageFilter.EDGE_ENHANCE_MORE)
    filter(ImageFilter.EMBOSS)
    filter(ImageFilter.FIND_EDGES)
    filter(ImageFilter.SMOOTH)
    filter(ImageFilter.SMOOTH_MORE)
    filter(ImageFilter.SHARPEN)
    filter(ImageFilter.MaxFilter)
    filter(ImageFilter.MedianFilter)
    filter(ImageFilter.MinFilter)
    filter(ImageFilter.ModeFilter)
    filter(ImageFilter.Kernel((3, 3), list(range(9))))

    assert_exception(TypeError, lambda: filter("hello"))

def test_crash():

    # crashes on small images
    im = Image.new("RGB", (1, 1))
    assert_no_exception(lambda: im.filter(ImageFilter.SMOOTH))

    im = Image.new("RGB", (2, 2))
    assert_no_exception(lambda: im.filter(ImageFilter.SMOOTH))

    im = Image.new("RGB", (3, 3))
    assert_no_exception(lambda: im.filter(ImageFilter.SMOOTH))

def test_modefilter():

    def modefilter(mode):
        im = Image.new(mode, (3, 3), None)
        im.putdata(list(range(9)))
        # image is:
        #   0 1 2
        #   3 4 5
        #   6 7 8
        mod = im.filter(ImageFilter.ModeFilter).getpixel((1, 1))
        im.putdata([0, 0, 1, 2, 5, 1, 5, 2, 0]) # mode=0
        mod2 = im.filter(ImageFilter.ModeFilter).getpixel((1, 1))
        return mod, mod2

    assert_equal(modefilter("1"), (4, 0))
    assert_equal(modefilter("L"), (4, 0))
    assert_equal(modefilter("P"), (4, 0))
    assert_equal(modefilter("RGB"), ((4, 0, 0), (0, 0, 0)))

def test_rankfilter():

    def rankfilter(mode):
        im = Image.new(mode, (3, 3), None)
        im.putdata(list(range(9)))
        # image is:
        #   0 1 2
        #   3 4 5
        #   6 7 8
        min = im.filter(ImageFilter.MinFilter).getpixel((1, 1))
        med = im.filter(ImageFilter.MedianFilter).getpixel((1, 1))
        max = im.filter(ImageFilter.MaxFilter).getpixel((1, 1))
        return min, med, max

    assert_equal(rankfilter("1"), (0, 4, 8))
    assert_equal(rankfilter("L"), (0, 4, 8))
    assert_exception(ValueError, lambda: rankfilter("P"))
    assert_equal(rankfilter("RGB"), ((0, 0, 0), (4, 0, 0), (8, 0, 0)))
    assert_equal(rankfilter("I"), (0, 4, 8))
    assert_equal(rankfilter("F"), (0.0, 4.0, 8.0))
