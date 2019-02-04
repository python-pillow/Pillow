from .helper import PillowTestCase, hopper
from PIL import Image


class TestImageThumbnail(PillowTestCase):

    def test_sanity(self):

        im = hopper()
        im.thumbnail((100, 100))

        self.assert_image(im, im.mode, (100, 100))

    def test_aspect(self):

        im = hopper()
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (100, 100))

        im = hopper().resize((128, 256))
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (50, 100))

        im = hopper().resize((128, 256))
        im.thumbnail((50, 100))
        self.assert_image(im, im.mode, (50, 100))

        im = hopper().resize((256, 128))
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (100, 50))

        im = hopper().resize((256, 128))
        im.thumbnail((100, 50))
        self.assert_image(im, im.mode, (100, 50))

        im = hopper().resize((128, 128))
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (100, 100))

    def test_no_resize(self):
        # Check that draft() can resize the image to the destination size
        im = Image.open("Tests/images/hopper.jpg")
        im.draft(None, (64, 64))
        self.assertEqual(im.size, (64, 64))

        # Test thumbnail(), where only draft() is necessary to resize the image
        im = Image.open("Tests/images/hopper.jpg")
        im.thumbnail((64, 64))
        self.assert_image(im, im.mode, (64, 64))
