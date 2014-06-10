from helper import unittest, PillowTestCase, tearDownModule, lena

import sys

from PIL import Image


class TestImagePutData(PillowTestCase):

    def test_sanity(self):

        im1 = lena()

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


if __name__ == '__main__':
    unittest.main()

# End of file
