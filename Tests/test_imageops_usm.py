from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter

im = Image.open("Tests/images/hopper.ppm")
snakes = Image.open("Tests/images/color_snakes.png")


class TestImageOpsUsm(PillowTestCase):

    def test_ops_api(self):

        i = ImageOps.gaussian_blur(im, 2.0)
        self.assertEqual(i.mode, "RGB")
        self.assertEqual(i.size, (128, 128))
        # i.save("blur.bmp")

        i = ImageOps.unsharp_mask(im, 2.0, 125, 8)
        self.assertEqual(i.mode, "RGB")
        self.assertEqual(i.size, (128, 128))
        # i.save("usm.bmp")

    def test_filter_api(self):

        filter = ImageFilter.GaussianBlur(2.0)
        i = im.filter(filter)
        self.assertEqual(i.mode, "RGB")
        self.assertEqual(i.size, (128, 128))

        filter = ImageFilter.UnsharpMask(2.0, 125, 8)
        i = im.filter(filter)
        self.assertEqual(i.mode, "RGB")
        self.assertEqual(i.size, (128, 128))

    def test_usm_formats(self):

        usm = ImageOps.unsharp_mask
        self.assertRaises(ValueError, lambda: usm(im.convert("1")))
        usm(im.convert("L"))
        self.assertRaises(ValueError, lambda: usm(im.convert("I")))
        self.assertRaises(ValueError, lambda: usm(im.convert("F")))
        usm(im.convert("RGB"))
        usm(im.convert("RGBA"))
        usm(im.convert("CMYK"))
        self.assertRaises(ValueError, lambda: usm(im.convert("YCbCr")))

    def test_blur_formats(self):

        blur = ImageOps.gaussian_blur
        self.assertRaises(ValueError, lambda: blur(im.convert("1")))
        blur(im.convert("L"))
        self.assertRaises(ValueError, lambda: blur(im.convert("I")))
        self.assertRaises(ValueError, lambda: blur(im.convert("F")))
        blur(im.convert("RGB"))
        blur(im.convert("RGBA"))
        blur(im.convert("CMYK"))
        self.assertRaises(ValueError, lambda: blur(im.convert("YCbCr")))

    def test_usm_accuracy(self):

        src = snakes.convert('RGB')
        i = src._new(ImageOps.unsharp_mask(src, 5, 1024, 0))
        # Image should not be changed because it have only 0 and 255 levels.
        self.assertEqual(i.tobytes(), src.tobytes())

    def test_blur_accuracy(self):

        i = snakes._new(ImageOps.gaussian_blur(snakes, .4))
        # These pixels surrounded with pixels with 255 intensity.
        # They must be very close to 255.
        for x, y, c in [(1, 0, 1), (2, 0, 1), (7, 8, 1), (8, 8, 1), (2, 9, 1),
                        (7, 3, 0), (8, 3, 0), (5, 8, 0), (5, 9, 0), (1, 3, 0),
                        (4, 3, 2), (4, 2, 2)]:
            self.assertGreaterEqual(i.im.getpixel((x, y))[c], 250)
        # Fuzzy match.
        gp = lambda x, y: i.im.getpixel((x, y))
        self.assertTrue(236 <= gp(7, 4)[0] <= 239)
        self.assertTrue(236 <= gp(7, 5)[2] <= 239)
        self.assertTrue(236 <= gp(7, 6)[2] <= 239)
        self.assertTrue(236 <= gp(7, 7)[1] <= 239)
        self.assertTrue(236 <= gp(8, 4)[0] <= 239)
        self.assertTrue(236 <= gp(8, 5)[2] <= 239)
        self.assertTrue(236 <= gp(8, 6)[2] <= 239)
        self.assertTrue(236 <= gp(8, 7)[1] <= 239)

if __name__ == '__main__':
    unittest.main()

# End of file
