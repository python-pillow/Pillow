from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageThumbnail(PillowTestCase):
    def test_sanity(self):
        im = hopper()
        self.assertIsNone(im.thumbnail((100, 100)))

        self.assertEqual(im.size, (100, 100))

    def test_aspect(self):
        im = Image.new("L", (128, 128))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (100, 100))

        im = Image.new("L", (128, 256))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (50, 100))

        im = Image.new("L", (128, 256))
        im.thumbnail((50, 100))
        self.assertEqual(im.size, (50, 100))

        im = Image.new("L", (256, 128))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (100, 50))

        im = Image.new("L", (256, 128))
        im.thumbnail((100, 50))
        self.assertEqual(im.size, (100, 50))

        im = Image.new("L", (128, 128))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (100, 100))

        im = Image.new("L", (256, 162))  # ratio is 1.5802469136
        im.thumbnail((33, 33))
        self.assertEqual(im.size, (33, 21))  # ratio is 1.5714285714

        im = Image.new("L", (162, 256))  # ratio is 0.6328125
        im.thumbnail((33, 33))
        self.assertEqual(im.size, (21, 33))  # ratio is 0.6363636364

    def test_no_resize(self):
        # Check that draft() can resize the image to the destination size
        with Image.open("Tests/images/hopper.jpg") as im:
            im.draft(None, (64, 64))
            self.assertEqual(im.size, (64, 64))

        # Test thumbnail(), where only draft() is necessary to resize the image
        with Image.open("Tests/images/hopper.jpg") as im:
            im.thumbnail((64, 64))
            self.assertEqual(im.size, (64, 64))
