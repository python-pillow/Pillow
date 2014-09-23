from helper import unittest, PillowTestCase, hopper

from PIL import Image

Image.USE_CFFI_ACCESS = False


class TestImagePutPixel(PillowTestCase):

    def test_sanity(self):

        im1 = hopper()
        im2 = Image.new(im1.mode, im1.size, 0)

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pos = x, y
                im2.putpixel(pos, im1.getpixel(pos))

        self.assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)
        im2.readonly = 1

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pos = x, y
                im2.putpixel(pos, im1.getpixel(pos))

        self.assertFalse(im2.readonly)
        self.assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)

        pix1 = im1.load()
        pix2 = im2.load()

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pix2[x, y] = pix1[x, y]

        self.assert_image_equal(im1, im2)

    # see test_image_getpixel for more tests


if __name__ == '__main__':
    unittest.main()

# End of file
