import sys
from helper import unittest, PillowTestCase, hopper

from PIL import Image

# The the default version of PyPy in Trusty is PyPy 5.4.1.
# There is a known error in it: TypeError: PyPy does not yet implement the new buffer interface (issue #2163).
SKIP_5_4_1_PYPY = hasattr(sys, 'pypy_version_info') and (
    sys.pypy_version_info >= (5, 4, 1, 'final', 0))

im = hopper().resize((128, 100))


class TestImageArray(PillowTestCase):

    def test_toarray(self):
        def test(mode):
            ai = im.convert(mode).__array_interface__
            return ai['version'], ai["shape"], ai["typestr"], len(ai["data"])
        # self.assertEqual(test("1"), (3, (100, 128), '|b1', 1600))
        self.assertEqual(test("L"), (3, (100, 128), '|u1', 12800))

        # FIXME: wrong?
        self.assertEqual(test("I"), (3, (100, 128), Image._ENDIAN + 'i4', 51200))
        # FIXME: wrong?
        self.assertEqual(test("F"), (3, (100, 128), Image._ENDIAN + 'f4', 51200))

        self.assertEqual(test("LA"), (3, (100, 128, 2), '|u1', 25600))
        self.assertEqual(test("RGB"), (3, (100, 128, 3), '|u1', 38400))
        self.assertEqual(test("RGBA"), (3, (100, 128, 4), '|u1', 51200))
        self.assertEqual(test("RGBX"), (3, (100, 128, 4), '|u1', 51200))

    @unittest.skipIf(SKIP_5_4_1_PYPY, "PyPy does not yet implement the new buffer interface")
    def test_fromarray(self):

        class Wrapper(object):
            """ Class with API matching Image.fromarray """

            def __init__(self, img, arr_params):
                self.img = img
                self.__array_interface__ = arr_params

            def tobytes(self):
                return self.img.tobytes()

        def test(mode):
            i = im.convert(mode)
            a = i.__array_interface__
            a["strides"] = 1  # pretend it's non-contiguous
            # Make wrapper instance for image, new array interface
            wrapped = Wrapper(i, a)
            out = Image.fromarray(wrapped)
            return out.mode, out.size, list(i.getdata()) == list(out.getdata())

        # self.assertEqual(test("1"), ("1", (128, 100), True))
        self.assertEqual(test("L"), ("L", (128, 100), True))
        self.assertEqual(test("I"), ("I", (128, 100), True))
        self.assertEqual(test("F"), ("F", (128, 100), True))
        self.assertEqual(test("LA"), ("LA", (128, 100), True))
        self.assertEqual(test("RGB"), ("RGB", (128, 100), True))
        self.assertEqual(test("RGBA"), ("RGBA", (128, 100), True))
        self.assertEqual(test("RGBX"), ("RGBA", (128, 100), True))


if __name__ == '__main__':
    unittest.main()
