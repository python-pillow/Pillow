from tester import *

from PIL import Image

def test_sanity():
    im1 = lena()
    im2 = Image.frombytes(im1.mode, im1.size, im1.tobytes())

    assert_image_equal(im1, im2)

