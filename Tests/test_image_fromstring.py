from tester import *

from PIL import Image

def test_sanity():

    im1 = lena()
    im2 = None

    if py3:
        im2 = Image.frombytes(im1.mode, im1.size, im1.tobytes())
    else:
        im2 = Image.fromstring(im1.mode, im1.size, im1.tostring())

    assert_image_equal(im1, im2)

