from PIL import Image

from .helper import PillowTestCase, hopper, fromstring, tostring


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

    def test_DCT_scaling_edges(self):
        # Make an image with red borders with size (N * 8) + 1 to cross DCT grid
        im = Image.new('RGB', (97, 97), 'red')
        im.paste(Image.new('RGB', (95, 95)), (1, 1))

        thumb = fromstring(tostring(im, "JPEG", quality=95))
        thumb.thumbnail((24, 24), Image.BICUBIC)

        ref = im.resize((24, 24), Image.BICUBIC)
        self.assert_image_similar(thumb, ref, 2)
