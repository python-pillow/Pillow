from tester import *

from PIL import Image

if hasattr(sys, 'pypy_version_info'):
    # This takes _forever_ on pypy. Open Bug,
    # see https://github.com/python-imaging/Pillow/issues/484
    skip()

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


def test_16bit_lut():
    """ Tests for 16 bit -> 8 bit lut for converting I->L images
        see https://github.com/python-imaging/Pillow/issues/440
    """

    im = lena("I")
    assert_no_exception(lambda: im.point(list(range(256))*256, 'L'))
