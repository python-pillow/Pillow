from helper import unittest, PillowTestCase, lena

from PIL import Image


class TestImage(PillowTestCase):

def test_sanity(self):

    self.assertRaises(ValueError, lambda: lena().tobitmap())
    assert_no_exception(lambda: lena().convert("1").tobitmap())

    im1 = lena().convert("1")

    bitmap = im1.tobitmap()

    assert_true(isinstance(bitmap, bytes))
    assert_image_equal(im1, fromstring(bitmap))


if __name__ == '__main__':
    unittest.main()

# End of file
