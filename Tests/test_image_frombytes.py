from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageFromBytes(PillowTestCase):

    def test_sanity(self):
        im1 = hopper()
        im2 = Image.frombytes(im1.mode, im1.size, im1.tobytes())

        self.assert_image_equal(im1, im2)


if __name__ == '__main__':
    unittest.main()
