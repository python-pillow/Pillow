from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageFromBytes(PillowTestCase):
    def test_sanity(self):
        im1 = hopper()
        im2 = Image.frombytes(im1.mode, im1.size, im1.tobytes())

        self.assert_image_equal(im1, im2)

    def test_not_implemented(self):
        self.assertRaises(NotImplementedError, Image.fromstring)
