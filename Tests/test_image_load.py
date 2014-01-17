from tester import *

from PIL import Image

def test_sanity():

    im = lena()

    pix = im.load()

    assert_equal(pix[0, 0], (223, 162, 133))
