from tester import *

from PIL import Image

def test_resize():
    def resize(mode, size):
        out = lena(mode).resize(size)
        assert_equal(out.mode, mode)
        assert_equal(out.size, size)
    for mode in "1", "P", "L", "RGB", "I", "F":
        yield_test(resize, mode, (100, 100))
        yield_test(resize, mode, (200, 200))
