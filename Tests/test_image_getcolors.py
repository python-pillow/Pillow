from tester import *

from PIL import Image

def test_getcolors():

    def getcolors(mode, limit=None):
        im = lena(mode)
        if limit:
            colors = im.getcolors(limit)
        else:
            colors = im.getcolors()
        if colors:
            return len(colors)
        return None

    assert_equal(getcolors("1"), 2)
    assert_equal(getcolors("L"), 193)
    assert_equal(getcolors("I"), 193)
    assert_equal(getcolors("F"), 193)
    assert_equal(getcolors("P"), 54) # fixed palette
    assert_equal(getcolors("RGB"), None)
    assert_equal(getcolors("RGBA"), None)
    assert_equal(getcolors("CMYK"), None)
    assert_equal(getcolors("YCbCr"), None)

    assert_equal(getcolors("L", 128), None)
    assert_equal(getcolors("L", 1024), 193)

    assert_equal(getcolors("RGB", 8192), None)
    assert_equal(getcolors("RGB", 16384), 14836)
    assert_equal(getcolors("RGB", 100000), 14836)

    assert_equal(getcolors("RGBA", 16384), 14836)
    assert_equal(getcolors("CMYK", 16384), 14836)
    assert_equal(getcolors("YCbCr", 16384), 11995)

# --------------------------------------------------------------------

def test_pack():
    # Pack problems for small tables (@PIL209)

    im = lena().quantize(3).convert("RGB")

    expected = [(3236, (227, 183, 147)), (6297, (143, 84, 81)), (6851, (208, 143, 112))]

    A = im.getcolors(maxcolors=2)
    assert_equal(A, None)

    A = im.getcolors(maxcolors=3)
    A.sort()
    assert_equal(A, expected)

    A = im.getcolors(maxcolors=4)
    A.sort()
    assert_equal(A, expected)

    A = im.getcolors(maxcolors=8)
    A.sort()
    assert_equal(A, expected)

    A = im.getcolors(maxcolors=16)
    A.sort()
    assert_equal(A, expected)
