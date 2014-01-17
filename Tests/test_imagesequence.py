from tester import *

from PIL import Image
from PIL import ImageSequence

def test_sanity():

    file = tempfile("temp.im")

    im = lena("RGB")
    im.save(file)

    seq = ImageSequence.Iterator(im)

    index = 0
    for frame in seq:
        assert_image_equal(im, frame)
        assert_equal(im.tell(), index)
        index = index + 1

    assert_equal(index, 1)

