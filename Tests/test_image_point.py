from helper import unittest, PillowTestCase, lena

import sys


class TestImagePoint(PillowTestCase):

    def test_sanity(self):
        im = lena()

        self.assertRaises(ValueError, lambda: im.point(list(range(256))))
        im.point(list(range(256))*3)
        im.point(lambda x: x)

        im = im.convert("I")
        self.assertRaises(ValueError, lambda: im.point(list(range(256))))
        im.point(lambda x: x*1)
        im.point(lambda x: x+1)
        im.point(lambda x: x*1+1)
        self.assertRaises(TypeError, lambda: im.point(lambda x: x-1))
        self.assertRaises(TypeError, lambda: im.point(lambda x: x/1))

    def test_16bit_lut(self):
        """ Tests for 16 bit -> 8 bit lut for converting I->L images
            see https://github.com/python-pillow/Pillow/issues/440
            """
        # This takes _forever_ on PyPy. Open Bug,
        # see https://github.com/python-pillow/Pillow/issues/484
        self.skipKnownBadTest(msg="Too Slow on pypy", interpreter='pypy')

        im = lena("I")
        im.point(list(range(256))*256, 'L')


if __name__ == '__main__':
    unittest.main()

# End of file
