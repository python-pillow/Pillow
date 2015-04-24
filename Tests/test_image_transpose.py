import helper
from helper import unittest, PillowTestCase

from PIL.Image import (FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, ROTATE_90, ROTATE_180,
                       ROTATE_270, TRANSPOSE)


class TestImageTranspose(PillowTestCase):

    hopper = {
        'L': helper.hopper('L').crop((0, 0, 121, 127)).copy(),
        'RGB': helper.hopper('RGB').crop((0, 0, 121, 127)).copy(),
    }

    def test_flip_left_right(self):
        def transpose(mode):
            im = self.hopper[mode]
            out = im.transpose(FLIP_LEFT_RIGHT)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)

            x, y = im.size
            self.assertEqual(im.getpixel((1, 1)), out.getpixel((x-2, 1)))
            self.assertEqual(im.getpixel((x-2, 1)), out.getpixel((1, 1)))
            self.assertEqual(im.getpixel((1, y-2)), out.getpixel((x-2, y-2)))
            self.assertEqual(im.getpixel((x-2, y-2)), out.getpixel((1, y-2)))

        for mode in ("L", "RGB"):
            transpose(mode)

    def test_flip_top_bottom(self):
        def transpose(mode):
            im = self.hopper[mode]
            out = im.transpose(FLIP_TOP_BOTTOM)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)

            x, y = im.size
            self.assertEqual(im.getpixel((1, 1)), out.getpixel((1, y-2)))
            self.assertEqual(im.getpixel((x-2, 1)), out.getpixel((x-2, y-2)))
            self.assertEqual(im.getpixel((1, y-2)), out.getpixel((1, 1)))
            self.assertEqual(im.getpixel((x-2, y-2)), out.getpixel((x-2, 1)))

        for mode in ("L", "RGB"):
            transpose(mode)

    def test_rotate_90(self):
        def transpose(mode):
            im = self.hopper[mode]
            out = im.transpose(ROTATE_90)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size[::-1])

            x, y = im.size
            self.assertEqual(im.getpixel((1, 1)), out.getpixel((1, x-2)))
            self.assertEqual(im.getpixel((x-2, 1)), out.getpixel((1, 1)))
            self.assertEqual(im.getpixel((1, y-2)), out.getpixel((y-2, x-2)))
            self.assertEqual(im.getpixel((x-2, y-2)), out.getpixel((y-2, 1)))

        for mode in ("L", "RGB"):
            transpose(mode)

    def test_rotate_180(self):
        def transpose(mode):
            im = self.hopper[mode]
            out = im.transpose(ROTATE_180)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)

            x, y = im.size
            self.assertEqual(im.getpixel((1, 1)), out.getpixel((x-2, y-2)))
            self.assertEqual(im.getpixel((x-2, 1)), out.getpixel((1, y-2)))
            self.assertEqual(im.getpixel((1, y-2)), out.getpixel((x-2, 1)))
            self.assertEqual(im.getpixel((x-2, y-2)), out.getpixel((1, 1)))

        for mode in ("L", "RGB"):
            transpose(mode)

    def test_rotate_270(self):
        def transpose(mode):
            im = self.hopper[mode]
            out = im.transpose(ROTATE_270)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size[::-1])

            x, y = im.size
            self.assertEqual(im.getpixel((1, 1)), out.getpixel((y-2, 1)))
            self.assertEqual(im.getpixel((x-2, 1)), out.getpixel((y-2, x-2)))
            self.assertEqual(im.getpixel((1, y-2)), out.getpixel((1, 1)))
            self.assertEqual(im.getpixel((x-2, y-2)), out.getpixel((1, x-2)))

        for mode in ("L", "RGB"):
            transpose(mode)

    def test_transpose(self):
        def transpose(mode):
            im = self.hopper[mode]
            out = im.transpose(TRANSPOSE)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size[::-1])

            x, y = im.size
            self.assertEqual(im.getpixel((1, 1)), out.getpixel((1, 1)))
            self.assertEqual(im.getpixel((x-2, 1)), out.getpixel((1, x-2)))
            self.assertEqual(im.getpixel((1, y-2)), out.getpixel((y-2, 1)))
            self.assertEqual(im.getpixel((x-2, y-2)), out.getpixel((y-2, x-2)))

        for mode in ("L", "RGB"):
            transpose(mode)

    def test_roundtrip(self):
        im = self.hopper['L']

        def transpose(first, second):
            return im.transpose(first).transpose(second)

        self.assert_image_equal(
            im, transpose(FLIP_LEFT_RIGHT, FLIP_LEFT_RIGHT))
        self.assert_image_equal(
            im, transpose(FLIP_TOP_BOTTOM, FLIP_TOP_BOTTOM))
        self.assert_image_equal(im, transpose(ROTATE_90, ROTATE_270))
        self.assert_image_equal(im, transpose(ROTATE_180, ROTATE_180))
        self.assert_image_equal(
            im.transpose(TRANSPOSE), transpose(ROTATE_90, FLIP_TOP_BOTTOM))
        self.assert_image_equal(
            im.transpose(TRANSPOSE), transpose(ROTATE_270, FLIP_LEFT_RIGHT))


if __name__ == '__main__':
    unittest.main()
