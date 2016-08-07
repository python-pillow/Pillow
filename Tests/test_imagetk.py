from helper import unittest, PillowTestCase
from PIL import Image

try:
    from PIL import ImageTk
    dir(ImageTk)
except (OSError, ImportError) as v:
    # Skipped via setUp()
    pass


class TestImageTk(PillowTestCase):

    def setUp(self):
        try:
            from PIL import ImageTk
            dir(ImageTk)
        except (OSError, ImportError) as v:
            self.skipTest(v)

    def test_kw(self):
        TEST_JPG = "Tests/images/hopper.jpg"
        TEST_PNG = "Tests/images/hopper.png"
        im1 = Image.open(TEST_JPG)
        im2 = Image.open(TEST_PNG)
        with open(TEST_PNG, 'rb') as fp:
            data = fp.read()
        kw = {"file": TEST_JPG, "data": data}

        # Test "file"
        im = ImageTk._get_image_from_kw(kw)
        self.assert_image_equal(im, im1)

        # Test "data"
        im = ImageTk._get_image_from_kw(kw)
        self.assert_image_equal(im, im2)

        # Test no relevant entry
        im = ImageTk._get_image_from_kw(kw)
        self.assertEqual(im, None)


if __name__ == '__main__':
    unittest.main()
