from helper import unittest, PillowTestCase, lena

try:
    import cffi

    from PIL import Image, PyAccess

    import test_image_putpixel as put
    import test_image_getpixel as get

    class TestCffi(PillowTestCase):

        Image.USE_CFFI_ACCESS = True

        def test_put(self):
            put.test_sanity()

        def test_get(self):
            get.test_basic()
            get.test_signedness()

        def _test_get_access(self, im):
            """ Do we get the same thing as the old pixel access """

            """ Using private interfaces, forcing a capi access and a pyaccess
            for the same image """
            caccess = im.im.pixel_access(False)
            access = PyAccess.new(im, False)

            w, h = im.size
            for x in range(0, w, 10):
                for y in range(0, h, 10):
                    self.assertEqual(access[(x, y)], caccess[(x, y)])

        def test_get_vs_c(self):
            self._test_get_access(lena('RGB'))
            self._test_get_access(lena('RGBA'))
            self._test_get_access(lena('L'))
            self._test_get_access(lena('LA'))
            self._test_get_access(lena('1'))
            self._test_get_access(lena('P'))
            # PA   -- how do I make a PA image???
            # self._test_get_access(lena('PA'))
            self._test_get_access(lena('F'))

            im = Image.new('I;16', (10, 10), 40000)
            self._test_get_access(im)
            im = Image.new('I;16L', (10, 10), 40000)
            self._test_get_access(im)
            im = Image.new('I;16B', (10, 10), 40000)
            self._test_get_access(im)

            im = Image.new('I', (10, 10), 40000)
            self._test_get_access(im)
            # These don't actually appear to be modes that I can actually make,
            # as unpack sets them directly into the I mode.
            # im = Image.new('I;32L', (10, 10), -2**10)
            # self._test_get_access(im)
            # im = Image.new('I;32B', (10, 10), 2**10)
            # self._test_get_access(im)

        def _test_set_access(self, im, color):
            """ Are we writing the correct bits into the image? """

            """ Using private interfaces, forcing a capi access and a pyaccess
            for the same image """
            caccess = im.im.pixel_access(False)
            access = PyAccess.new(im, False)

            w, h = im.size
            for x in range(0, w, 10):
                for y in range(0, h, 10):
                    access[(x, y)] = color
                    self.assertEqual(color, caccess[(x, y)])

        def test_set_vs_c(self):
            self._test_set_access(lena('RGB'), (255, 128, 0))
            self._test_set_access(lena('RGBA'), (255, 192, 128, 0))
            self._test_set_access(lena('L'), 128)
            self._test_set_access(lena('LA'), (128, 128))
            self._test_set_access(lena('1'), 255)
            self._test_set_access(lena('P'), 128)
            # self._test_set_access(i, (128, 128)) #PA  -- undone how to make
            self._test_set_access(lena('F'), 1024.0)

            im = Image.new('I;16', (10, 10), 40000)
            self._test_set_access(im, 45000)
            im = Image.new('I;16L', (10, 10), 40000)
            self._test_set_access(im, 45000)
            im = Image.new('I;16B', (10, 10), 40000)
            self._test_set_access(im, 45000)

            im = Image.new('I', (10, 10), 40000)
            self._test_set_access(im, 45000)
            # im = Image.new('I;32L', (10, 10), -(2**10))
            # self._test_set_access(im, -(2**13)+1)
            # im = Image.new('I;32B', (10, 10), 2**10)
            # self._test_set_access(im, 2**13-1)

except ImportError:
    class TestCffi(PillowTestCase):
        def test_skip(self):
            self.skipTest("ImportError")


if __name__ == '__main__':
    unittest.main()

# End of file
