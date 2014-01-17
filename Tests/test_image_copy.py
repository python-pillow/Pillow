from tester import *

from PIL import Image

def test_copy():
    def copy(mode):
        im = lena(mode)
        out = im.copy()
        assert_equal(out.mode, mode)
        assert_equal(out.size, im.size)
    for mode in "1", "P", "L", "RGB", "I", "F":
        yield_test(copy, mode)
