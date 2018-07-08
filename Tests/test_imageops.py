from helper import unittest, PillowTestCase, hopper

from PIL import ImageOps
from PIL import Image


class TestImageOps(PillowTestCase):

    class Deformer(object):
        def getmesh(self, im):
            x, y = im.size
            return [((0, 0, x, y), (0, 0, x, 0, x, y, y, 0))]

    deformer = Deformer()

    def test_sanity(self):

        ImageOps.autocontrast(hopper("L"))
        ImageOps.autocontrast(hopper("RGB"))

        ImageOps.autocontrast(hopper("L"), cutoff=10)
        ImageOps.autocontrast(hopper("L"), ignore=[0, 255])

        ImageOps.colorize(hopper("L"), (0, 0, 0), (255, 255, 255))
        ImageOps.colorize(hopper("L"), "black", "white")

        ImageOps.crop(hopper("L"), 1)
        ImageOps.crop(hopper("RGB"), 1)

        ImageOps.deform(hopper("L"), self.deformer)
        ImageOps.deform(hopper("RGB"), self.deformer)

        ImageOps.equalize(hopper("L"))
        ImageOps.equalize(hopper("RGB"))

        ImageOps.expand(hopper("L"), 1)
        ImageOps.expand(hopper("RGB"), 1)
        ImageOps.expand(hopper("L"), 2, "blue")
        ImageOps.expand(hopper("RGB"), 2, "blue")

        ImageOps.fit(hopper("L"), (128, 128))
        ImageOps.fit(hopper("RGB"), (128, 128))

        ImageOps.flip(hopper("L"))
        ImageOps.flip(hopper("RGB"))

        ImageOps.grayscale(hopper("L"))
        ImageOps.grayscale(hopper("RGB"))

        ImageOps.invert(hopper("L"))
        ImageOps.invert(hopper("RGB"))

        ImageOps.mirror(hopper("L"))
        ImageOps.mirror(hopper("RGB"))

        ImageOps.posterize(hopper("L"), 4)
        ImageOps.posterize(hopper("RGB"), 4)

        ImageOps.solarize(hopper("L"))
        ImageOps.solarize(hopper("RGB"))

    def test_1pxfit(self):
        # Division by zero in equalize if image is 1 pixel high
        newimg = ImageOps.fit(hopper("RGB").resize((1, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((1, 100)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((100, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

    def test_pil163(self):
        # Division by zero in equalize if < 255 pixels in image (@PIL163)

        i = hopper("RGB").resize((15, 16))

        ImageOps.equalize(i.convert("L"))
        ImageOps.equalize(i.convert("P"))
        ImageOps.equalize(i.convert("RGB"))

    def test_scale(self):
        # Test the scaling function
        i = hopper("L").resize((50, 50))

        with self.assertRaises(ValueError):
            ImageOps.scale(i, -1)

        newimg = ImageOps.scale(i, 1)
        self.assertEqual(newimg.size, (50, 50))

        newimg = ImageOps.scale(i, 2)
        self.assertEqual(newimg.size, (100, 100))

        newimg = ImageOps.scale(i, 0.5)
        self.assertEqual(newimg.size, (25, 25))

    def test_colorize(self):
        # Test the colorizing function

        # Open test image (256px by 10px, black to white)
        im = Image.open("Tests/images/bw_gradient.png")
        im = im.convert("L")

        # Create image with original 2-color functionality
        im_2c = ImageOps.colorize(im, 'red', 'green')

        # Create image with original 2-color functionality with offsets
        im_2c_offset = ImageOps.colorize(im,
                                         black='red',
                                         white='green',
                                         blackpoint=50,
                                         whitepoint=200)

        # Create image with new three color functionality with offsets
        im_3c_offset = ImageOps.colorize(im,
                                         black='red',
                                         white='green',
                                         mid='blue',
                                         blackpoint=50,
                                         whitepoint=200,
                                         midpoint=100)

        # Define function for approximate equality of tuples
        def tuple_approx_equal(actual, target, thresh):
            value = True
            for i, target in enumerate(target):
                value *= (target - thresh <= actual[i] <= target + thresh)
            return value

        # Test output image (2-color)
        left = (0, 1)
        middle = (127, 1)
        right = (255, 1)
        self.assertTrue(tuple_approx_equal(im_2c.getpixel(left),
                                           (255, 0, 0), thresh=1),
                        '2-color image black incorrect')
        self.assertTrue(tuple_approx_equal(im_2c.getpixel(middle),
                                           (127, 63, 0), thresh=1),
                        '2-color image mid incorrect')
        self.assertTrue(tuple_approx_equal(im_2c.getpixel(right),
                                           (0, 127, 0), thresh=1),
                        '2-color image white incorrect')

        # Test output image (2-color) with offsets
        left = (25, 1)
        middle = (125, 1)
        right = (225, 1)
        self.assertTrue(tuple_approx_equal(im_2c_offset.getpixel(left),
                                           (255, 0, 0), thresh=1),
                        '2-color image (with offset) black incorrect')
        self.assertTrue(tuple_approx_equal(im_2c_offset.getpixel(middle),
                                           (127, 63, 0), thresh=1),
                        '2-color image (with offset) mid incorrect')
        self.assertTrue(tuple_approx_equal(im_2c_offset.getpixel(right),
                                           (0, 127, 0), thresh=1),
                        '2-color image (with offset) white incorrect')

        # Test output image (3-color) with offsets
        left = (25, 1)
        left_middle = (75, 1)
        middle = (100, 1)
        right_middle = (150, 1)
        right = (225, 1)
        self.assertTrue(tuple_approx_equal(im_3c_offset.getpixel(left),
                                           (255, 0, 0), thresh=1),
                        '3-color image (with offset) black incorrect')
        self.assertTrue(tuple_approx_equal(im_3c_offset.getpixel(left_middle),
                                           (127, 0, 127), thresh=1),
                        '3-color image (with offset) low-mid incorrect')
        self.assertTrue(tuple_approx_equal(im_3c_offset.getpixel(middle),
                                           (0, 0, 255), thresh=1),
                        '3-color image (with offset) mid incorrect')
        self.assertTrue(tuple_approx_equal(im_3c_offset.getpixel(right_middle),
                                           (0, 63, 127), thresh=1),
                        '3-color image (with offset) high-mid incorrect')
        self.assertTrue(tuple_approx_equal(im_3c_offset.getpixel(right),
                                           (0, 127, 0), thresh=1),
                        '3-color image (with offset) white incorrect')


if __name__ == '__main__':
    unittest.main()
