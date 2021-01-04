from PIL import Image

from .helper import assert_image_equal, hopper


def test_sanity():
    im1 = hopper()
    im2 = Image.frombytes(im1.mode, im1.size, im1.tobytes())

    assert_image_equal(im1, im2)
