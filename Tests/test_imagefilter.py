from tester import *

from PIL import Image
from PIL import ImageFilter

def test_sanity():
    # see test_image_filter for more tests

    assert_no_exception(lambda: ImageFilter.MaxFilter)
    assert_no_exception(lambda: ImageFilter.MedianFilter)
    assert_no_exception(lambda: ImageFilter.MinFilter)
    assert_no_exception(lambda: ImageFilter.ModeFilter)
    assert_no_exception(lambda: ImageFilter.Kernel((3, 3), list(range(9))))
    assert_no_exception(lambda: ImageFilter.GaussianBlur)
    assert_no_exception(lambda: ImageFilter.GaussianBlur(5))
    assert_no_exception(lambda: ImageFilter.UnsharpMask)
    assert_no_exception(lambda: ImageFilter.UnsharpMask(10))

    assert_no_exception(lambda: ImageFilter.BLUR)
    assert_no_exception(lambda: ImageFilter.CONTOUR)
    assert_no_exception(lambda: ImageFilter.DETAIL)
    assert_no_exception(lambda: ImageFilter.EDGE_ENHANCE)
    assert_no_exception(lambda: ImageFilter.EDGE_ENHANCE_MORE)
    assert_no_exception(lambda: ImageFilter.EMBOSS)
    assert_no_exception(lambda: ImageFilter.FIND_EDGES)
    assert_no_exception(lambda: ImageFilter.SMOOTH)
    assert_no_exception(lambda: ImageFilter.SMOOTH_MORE)
    assert_no_exception(lambda: ImageFilter.SHARPEN)



