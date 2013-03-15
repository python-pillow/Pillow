from tester import *

from PIL import Image

def test_histogram():

    def histogram(mode):
        h = lena(mode).histogram()
        return len(h), min(h), max(h)

    assert_equal(histogram("1"), (256, 0, 8872))
    assert_equal(histogram("L"), (256, 0, 199))
    assert_equal(histogram("I"), (256, 0, 199))
    assert_equal(histogram("F"), (256, 0, 199))
    assert_equal(histogram("P"), (256, 0, 2912))
    assert_equal(histogram("RGB"), (768, 0, 285))
    assert_equal(histogram("RGBA"), (1024, 0, 16384))
    assert_equal(histogram("CMYK"), (1024, 0, 16384))
    assert_equal(histogram("YCbCr"), (768, 0, 741))
