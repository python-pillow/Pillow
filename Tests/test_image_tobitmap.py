from helper import unittest, PillowTestCase, tearDownModule, lena, fromstring


class TestImageToBitmap(PillowTestCase):

    def test_sanity(self):

        self.assertRaises(ValueError, lambda: lena().tobitmap())
        lena().convert("1").tobitmap()

        im1 = lena().convert("1")

        bitmap = im1.tobitmap()

        self.assertIsInstance(bitmap, bytes)
        self.assert_image_equal(im1, fromstring(bitmap))


if __name__ == '__main__':
    unittest.main()

# End of file
