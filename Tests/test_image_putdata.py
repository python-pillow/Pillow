from helper import unittest, PillowTestCase, hopper
from array import array

import sys

from PIL import Image


class TestImagePutData(PillowTestCase):

    def test_sanity(self):

        im1 = hopper()

        data = list(im1.getdata())

        im2 = Image.new(im1.mode, im1.size, 0)
        im2.putdata(data)

        self.assert_image_equal(im1, im2)

        # readonly
        im2 = Image.new(im1.mode, im2.size, 0)
        im2.readonly = 1
        im2.putdata(data)

        self.assertFalse(im2.readonly)
        self.assert_image_equal(im1, im2)

    def test_long_integers(self):
        # see bug-200802-systemerror
        def put(value):
            im = Image.new("RGBA", (1, 1))
            im.putdata([value])
            return im.getpixel((0, 0))
        self.assertEqual(put(0xFFFFFFFF), (255, 255, 255, 255))
        self.assertEqual(put(0xFFFFFFFF), (255, 255, 255, 255))
        self.assertEqual(put(-1), (255, 255, 255, 255))
        self.assertEqual(put(-1), (255, 255, 255, 255))
        if sys.maxsize > 2**32:
            self.assertEqual(put(sys.maxsize), (255, 255, 255, 255))
        else:
            self.assertEqual(put(sys.maxsize), (255, 255, 255, 127))

    def test_pypy_performance(self):
        im = Image.new('L', (256, 256))
        im.putdata(list(range(256))*256)

    def test_mode_i(self):
        src = hopper('L')
        data = list(src.getdata())
        im = Image.new('I', src.size, 0)
        im.putdata(data, 2, 256)

        target = [2 * elt + 256 for elt in data]
        self.assertEqual(list(im.getdata()), target)

    def test_mode_F(self):
        src = hopper('L')
        data = list(src.getdata())
        im = Image.new('F', src.size, 0)
        im.putdata(data, 2.0, 256.0)

        target = [2.0 * float(elt) + 256.0 for elt in data]
        self.assertEqual(list(im.getdata()), target)

    def test_array_B(self):
        # shouldn't segfault
        # see https://github.com/python-pillow/Pillow/issues/1008

        arr = array('B', [0])*15000
        im = Image.new('L', (150, 100))
        im.putdata(arr)

        self.assertEqual(len(im.getdata()), len(arr))

    def test_array_F(self):
        # shouldn't segfault
        # see https://github.com/python-pillow/Pillow/issues/1008

        im = Image.new('F', (150, 100))
        arr = array('f', [0.0])*15000
        im.putdata(arr)

        self.assertEqual(len(im.getdata()), len(arr))

if __name__ == '__main__':
    unittest.main()

# End of file
