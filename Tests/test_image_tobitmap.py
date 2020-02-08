from .helper import PillowTestCase, assert_image_equal, fromstring, hopper


class TestImageToBitmap(PillowTestCase):
    def test_sanity(self):

        self.assertRaises(ValueError, lambda: hopper().tobitmap())

        im1 = hopper().convert("1")

        bitmap = im1.tobitmap()

        self.assertIsInstance(bitmap, bytes)
        assert_image_equal(im1, fromstring(bitmap))
