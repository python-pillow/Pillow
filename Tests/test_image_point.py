from helper import unittest, PillowTestCase, hopper


class TestImagePoint(PillowTestCase):

    def test_sanity(self):
        im = hopper()

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
        # self.skipKnownBadTest(msg="Too Slow on pypy", interpreter='pypy')

        im = hopper("I")
        im.point(list(range(256))*256, 'L')

    def test_f_lut(self):
        """ Tests for floating point lut of 8bit gray image """
        im = hopper('L')
        lut = [0.5 * float(x) for x in range(256)]

        out = im.point(lut, 'F')

        int_lut = [x//2 for x in range(256)]
        self.assert_image_equal(out.convert('L'), im.point(int_lut, 'L'))


if __name__ == '__main__':
    unittest.main()

# End of file
