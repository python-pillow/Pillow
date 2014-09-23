from helper import unittest, PillowTestCase, hopper


class TestImageOffset(PillowTestCase):

    def test_offset(self):

        im1 = hopper()

        im2 = self.assert_warning(DeprecationWarning, lambda: im1.offset(10))
        self.assertEqual(im1.getpixel((0, 0)), im2.getpixel((10, 10)))

        im2 = self.assert_warning(
            DeprecationWarning, lambda: im1.offset(10, 20))
        self.assertEqual(im1.getpixel((0, 0)), im2.getpixel((10, 20)))

        im2 = self.assert_warning(
            DeprecationWarning, lambda: im1.offset(20, 20))
        self.assertEqual(im1.getpixel((0, 0)), im2.getpixel((20, 20)))


if __name__ == '__main__':
    unittest.main()

# End of file
