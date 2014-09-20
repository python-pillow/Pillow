from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter

im = Image.open("Tests/images/hopper.ppm")


class TestImageOpsUsm(PillowTestCase):

    def test_ops_api(self):

        i = ImageOps.gaussian_blur(im, 2.0)
        self.assertEqual(i.mode, "RGB")
        self.assertEqual(i.size, (128, 128))
        # i.save("blur.bmp")

        i = ImageOps.usm(im, 2.0, 125, 8)
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

    def test_usm(self):

        usm = ImageOps.unsharp_mask
        self.assertRaises(ValueError, lambda: usm(im.convert("1")))
        usm(im.convert("L"))
        self.assertRaises(ValueError, lambda: usm(im.convert("I")))
        self.assertRaises(ValueError, lambda: usm(im.convert("F")))
        usm(im.convert("RGB"))
        usm(im.convert("RGBA"))
        usm(im.convert("CMYK"))
        self.assertRaises(ValueError, lambda: usm(im.convert("YCbCr")))

    def test_blur(self):

        blur = ImageOps.gaussian_blur
        self.assertRaises(ValueError, lambda: blur(im.convert("1")))
        blur(im.convert("L"))
        self.assertRaises(ValueError, lambda: blur(im.convert("I")))
        self.assertRaises(ValueError, lambda: blur(im.convert("F")))
        blur(im.convert("RGB"))
        blur(im.convert("RGBA"))
        blur(im.convert("CMYK"))
        self.assertRaises(ValueError, lambda: blur(im.convert("YCbCr")))


if __name__ == '__main__':
    unittest.main()

# End of file
