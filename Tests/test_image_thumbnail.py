from helper import unittest, PillowTestCase, hopper


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


if __name__ == '__main__':
    unittest.main()

# End of file
