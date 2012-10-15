from tester import *

from PIL import Image

def test_sanity():

    im = lena()

    im = im.quantize()
    assert_image(im, "P", im.size)

    im = lena()
    im = im.quantize(palette=lena("P"))
    assert_image(im, "P", im.size)
    
