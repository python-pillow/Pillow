from helper import unittest, PillowTestCase, hopper

from PIL import Image

FLIP_LEFT_RIGHT = Image.FLIP_LEFT_RIGHT
FLIP_TOP_BOTTOM = Image.FLIP_TOP_BOTTOM
ROTATE_90 = Image.ROTATE_90
ROTATE_180 = Image.ROTATE_180
ROTATE_270 = Image.ROTATE_270


class TestImageTranspose(PillowTestCase):

    def test_sanity(self):

        im = hopper()

        im.transpose(FLIP_LEFT_RIGHT)
        im.transpose(FLIP_TOP_BOTTOM)

        im.transpose(ROTATE_90)
        im.transpose(ROTATE_180)
        im.transpose(ROTATE_270)

    def test_roundtrip(self):

        im = hopper()

        def transpose(first, second):
            return im.transpose(first).transpose(second)

        self.assert_image_equal(
            im, transpose(FLIP_LEFT_RIGHT, FLIP_LEFT_RIGHT))
        self.assert_image_equal(
            im, transpose(FLIP_TOP_BOTTOM, FLIP_TOP_BOTTOM))

        self.assert_image_equal(im, transpose(ROTATE_90, ROTATE_270))
        self.assert_image_equal(im, transpose(ROTATE_180, ROTATE_180))


if __name__ == '__main__':
    unittest.main()

# End of file
