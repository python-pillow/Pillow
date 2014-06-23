from helper import unittest, PillowTestCase, tearDownModule, lena


class TestImageThumbnail(PillowTestCase):

    def test_sanity(self):

        im = lena()
        im.thumbnail((100, 100))

        self.assert_image(im, im.mode, (100, 100))

    def test_aspect(self):

        im = lena()
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (100, 100))

        im = lena().resize((128, 256))
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (50, 100))

        im = lena().resize((128, 256))
        im.thumbnail((50, 100))
        self.assert_image(im, im.mode, (50, 100))

        im = lena().resize((256, 128))
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (100, 50))

        im = lena().resize((256, 128))
        im.thumbnail((100, 50))
        self.assert_image(im, im.mode, (100, 50))

        im = lena().resize((128, 128))
        im.thumbnail((100, 100))
        self.assert_image(im, im.mode, (100, 100))


if __name__ == '__main__':
    unittest.main()

# End of file
