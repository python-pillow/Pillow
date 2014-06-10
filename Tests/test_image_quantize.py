from tester import *

from PIL import Image

def test_sanity():

    im = lena()

    im = im.quantize()
    assert_image(im, "P", im.size)

    im = lena()
    im = im.quantize(palette=lena("P"))
    assert_image(im, "P", im.size)

def test_octree_quantize():
    im = lena()

    im = im.quantize(100, Image.FASTOCTREE)
    assert_image(im, "P", im.size)

    assert len(im.getcolors()) == 100

def test_rgba_quantize():
    im = lena('RGBA')
    assert_no_exception(lambda: im.quantize())
    assert_exception(Exception, lambda: im.quantize(method=0))
