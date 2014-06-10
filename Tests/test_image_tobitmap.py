from tester import *

from PIL import Image

def test_sanity():

    assert_exception(ValueError, lambda: lena().tobitmap())
    assert_no_exception(lambda: lena().convert("1").tobitmap())

    im1 = lena().convert("1")

    bitmap = im1.tobitmap()

    assert_true(isinstance(bitmap, bytes))
    assert_image_equal(im1, fromstring(bitmap))
