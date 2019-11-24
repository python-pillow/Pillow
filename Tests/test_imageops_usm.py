from PIL import Image, ImageFilter

from .helper import PillowTestCase


class TestImageOpsUsm(PillowTestCase):
    def setUp(self):
        super().setUp()
        self.im = Image.open("Tests/images/hopper.ppm")
        self.addCleanup(self.im.close)
        self.snakes = Image.open("Tests/images/color_snakes.png")
        self.addCleanup(self.snakes.close)

    def test_filter_api(self):

        test_filter = ImageFilter.GaussianBlur(2.0)
        i = self.im.filter(test_filter)
        self.assertEqual(i.mode, "RGB")
        self.assertEqual(i.size, (128, 128))

        test_filter = ImageFilter.UnsharpMask(2.0, 125, 8)
        i = self.im.filter(test_filter)
        self.assertEqual(i.mode, "RGB")
        self.assertEqual(i.size, (128, 128))

    def test_usm_formats(self):

        usm = ImageFilter.UnsharpMask
        self.assertRaises(ValueError, self.im.convert("1").filter, usm)
        self.im.convert("L").filter(usm)
        self.assertRaises(ValueError, self.im.convert("I").filter, usm)
        self.assertRaises(ValueError, self.im.convert("F").filter, usm)
        self.im.convert("RGB").filter(usm)
        self.im.convert("RGBA").filter(usm)
        self.im.convert("CMYK").filter(usm)
        self.assertRaises(ValueError, self.im.convert("YCbCr").filter, usm)

    def test_blur_formats(self):

        blur = ImageFilter.GaussianBlur
        self.assertRaises(ValueError, self.im.convert("1").filter, blur)
        blur(self.im.convert("L"))
        self.assertRaises(ValueError, self.im.convert("I").filter, blur)
        self.assertRaises(ValueError, self.im.convert("F").filter, blur)
        self.im.convert("RGB").filter(blur)
        self.im.convert("RGBA").filter(blur)
        self.im.convert("CMYK").filter(blur)
        self.assertRaises(ValueError, self.im.convert("YCbCr").filter, blur)

    def test_usm_accuracy(self):

        src = self.snakes.convert("RGB")
        i = src.filter(ImageFilter.UnsharpMask(5, 1024, 0))
        # Image should not be changed because it have only 0 and 255 levels.
        self.assertEqual(i.tobytes(), src.tobytes())

    def test_blur_accuracy(self):

        i = self.snakes.filter(ImageFilter.GaussianBlur(0.4))
        # These pixels surrounded with pixels with 255 intensity.
        # They must be very close to 255.
        for x, y, c in [
            (1, 0, 1),
            (2, 0, 1),
            (7, 8, 1),
            (8, 8, 1),
            (2, 9, 1),
            (7, 3, 0),
            (8, 3, 0),
            (5, 8, 0),
            (5, 9, 0),
            (1, 3, 0),
            (4, 3, 2),
            (4, 2, 2),
        ]:
            self.assertGreaterEqual(i.im.getpixel((x, y))[c], 250)
        # Fuzzy match.

        def gp(x, y):
            return i.im.getpixel((x, y))

        self.assertTrue(236 <= gp(7, 4)[0] <= 239)
        self.assertTrue(236 <= gp(7, 5)[2] <= 239)
        self.assertTrue(236 <= gp(7, 6)[2] <= 239)
        self.assertTrue(236 <= gp(7, 7)[1] <= 239)
        self.assertTrue(236 <= gp(8, 4)[0] <= 239)
        self.assertTrue(236 <= gp(8, 5)[2] <= 239)
        self.assertTrue(236 <= gp(8, 6)[2] <= 239)
        self.assertTrue(236 <= gp(8, 7)[1] <= 239)
