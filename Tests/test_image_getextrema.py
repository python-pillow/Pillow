from tester import *

from PIL import Image

def test_extrema():

    def extrema(mode):
        return lena(mode).getextrema()

    assert_equal(extrema("1"), (0, 255))
    assert_equal(extrema("L"), (40, 235))
    assert_equal(extrema("I"), (40, 235))
    assert_equal(extrema("F"), (40.0, 235.0))
    assert_equal(extrema("P"), (11, 218)) # fixed palette
    assert_equal(extrema("RGB"), ((61, 255), (26, 234), (44, 223)))
    assert_equal(extrema("RGBA"), ((61, 255), (26, 234), (44, 223), (255, 255)))
    assert_equal(extrema("CMYK"), ((0, 194), (21, 229), (32, 211), (0, 0)))
