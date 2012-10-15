from tester import *

from PIL import Image

def test_sanity():
    
    im = lena()

    assert_exception(ValueError, lambda: im.point(list(range(256))))
    assert_no_exception(lambda: im.point(list(range(256))*3))
    assert_no_exception(lambda: im.point(lambda x: x))

    im = im.convert("I")
    assert_exception(ValueError, lambda: im.point(list(range(256))))
    assert_no_exception(lambda: im.point(lambda x: x*1))
    assert_no_exception(lambda: im.point(lambda x: x+1))
    assert_no_exception(lambda: im.point(lambda x: x*1+1))
    assert_exception(TypeError, lambda: im.point(lambda x: x-1))
    assert_exception(TypeError, lambda: im.point(lambda x: x/1))
