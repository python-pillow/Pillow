from helper import unittest, PillowTestCase, hopper

try:
    import cffi
    from PIL import PyAccess
except ImportError:
    # Skip in setUp()
    pass

from PIL import Image

from test_image_putpixel import TestImagePutPixel
from test_image_getpixel import TestImageGetPixel

Image.USE_CFFI_ACCESS = True


class TestCffiPutPixel(TestImagePutPixel):

    def setUp(self):
        try:
            import cffi
        except ImportError:
            self.skipTest("No cffi")

    def test_put(self):
        self.test_sanity()


class TestCffiGetPixel(TestImageGetPixel):

    def setUp(self):
        try:
            import cffi
        except ImportError:
            self.skipTest("No cffi")

    def test_get(self):
        self.test_basic()
        self.test_signedness()


class TestCffi(PillowTestCase):

    def setUp(self):
        try:
            import cffi
        except ImportError:
            self.skipTest("No cffi")

    def _test_get_access(self, im):
        """Do we get the same thing as the old pixel access

        Using private interfaces, forcing a capi access and
        a pyaccess for the same image"""
        caccess = im.im.pixel_access(False)
        access = PyAccess.new(im, False)

        w, h = im.size
        for x in range(0, w, 10):
            for y in range(0, h, 10):
                self.assertEqual(access[(x, y)], caccess[(x, y)])

        # Access an out-of-range pixel
        self.assertRaises(ValueError,
                          lambda: access[(access.xsize+1, access.ysize+1)])

    def test_get_vs_c(self):
        rgb = hopper('RGB')
        rgb.load()
        self._test_get_access(rgb)
        self._test_get_access(hopper('RGBA'))
        self._test_get_access(hopper('L'))
        self._test_get_access(hopper('LA'))
        self._test_get_access(hopper('1'))
        self._test_get_access(hopper('P'))
        # self._test_get_access(hopper('PA')) # PA -- how do I make a PA image?
        self._test_get_access(hopper('F'))

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
        """Are we writing the correct bits into the image?

        Using private interfaces, forcing a capi access and
        a pyaccess for the same image"""
        caccess = im.im.pixel_access(False)
        access = PyAccess.new(im, False)

        w, h = im.size
        for x in range(0, w, 10):
            for y in range(0, h, 10):
                access[(x, y)] = color
                self.assertEqual(color, caccess[(x, y)])

        # Attempt to set the value on a read-only image
        access = PyAccess.new(im, True)
        try:
            access[(0, 0)] = color
        except ValueError:
            return
        self.fail("Putpixel did not fail on a read-only image")

    def test_set_vs_c(self):
        rgb = hopper('RGB')
        rgb.load()
        self._test_set_access(rgb, (255, 128, 0))
        self._test_set_access(hopper('RGBA'), (255, 192, 128, 0))
        self._test_set_access(hopper('L'), 128)
        self._test_set_access(hopper('LA'), (128, 128))
        self._test_set_access(hopper('1'), 255)
        self._test_set_access(hopper('P'), 128)
        # self._test_set_access(i, (128, 128))  #PA  -- undone how to make
        self._test_set_access(hopper('F'), 1024.0)

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


if __name__ == '__main__':
    unittest.main()

# End of file
