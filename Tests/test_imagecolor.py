from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageColor


class TestImageColor(PillowTestCase):

    def test_sanity(self):
        self.assertEqual((255, 0, 0), ImageColor.getrgb("#f00"))
        self.assertEqual((255, 0, 0), ImageColor.getrgb("#ff0000"))
        self.assertEqual((255, 0, 0), ImageColor.getrgb("rgb(255,0,0)"))
        self.assertEqual((255, 0, 0), ImageColor.getrgb("rgb(255, 0, 0)"))
        self.assertEqual((255, 0, 0), ImageColor.getrgb("rgb(100%,0%,0%)"))
        self.assertEqual((255, 0, 0), ImageColor.getrgb("hsl(0, 100%, 50%)"))
        self.assertEqual((255, 0, 0, 0), ImageColor.getrgb("rgba(255,0,0,0)"))
        self.assertEqual(
            (255, 0, 0, 0), ImageColor.getrgb("rgba(255, 0, 0, 0)"))
        self.assertEqual((255, 0, 0), ImageColor.getrgb("red"))

        self.assertRaises(ValueError,
                          lambda: ImageColor.getrgb("invalid color"))

    # look for rounding errors (based on code by Tim Hatch)
    def test_rounding_errors(self):

        for color in list(ImageColor.colormap.keys()):
            expected = Image.new(
                "RGB", (1, 1), color).convert("L").getpixel((0, 0))
            actual = Image.new("L", (1, 1), color).getpixel((0, 0))
            self.assertEqual(expected, actual)

        self.assertEqual((0, 0, 0), ImageColor.getcolor("black", "RGB"))
        self.assertEqual((255, 255, 255), ImageColor.getcolor("white", "RGB"))
        self.assertEqual(
            (0, 255, 115), ImageColor.getcolor("rgba(0, 255, 115, 33)", "RGB"))
        Image.new("RGB", (1, 1), "white")

        self.assertEqual((0, 0, 0, 255), ImageColor.getcolor("black", "RGBA"))
        self.assertEqual(
            (255, 255, 255, 255), ImageColor.getcolor("white", "RGBA"))
        self.assertEqual(
            (0, 255, 115, 33),
            ImageColor.getcolor("rgba(0, 255, 115, 33)", "RGBA"))
        Image.new("RGBA", (1, 1), "white")

        self.assertEqual(0, ImageColor.getcolor("black", "L"))
        self.assertEqual(255, ImageColor.getcolor("white", "L"))
        self.assertEqual(162,
                         ImageColor.getcolor("rgba(0, 255, 115, 33)", "L"))
        Image.new("L", (1, 1), "white")

        self.assertEqual(0, ImageColor.getcolor("black", "1"))
        self.assertEqual(255, ImageColor.getcolor("white", "1"))
        # The following test is wrong, but is current behavior
        # The correct result should be 255 due to the mode 1
        self.assertEqual(
            162, ImageColor.getcolor("rgba(0, 255, 115, 33)", "1"))
        # Correct behavior
        # self.assertEqual(
        #     255, ImageColor.getcolor("rgba(0, 255, 115, 33)", "1"))
        Image.new("1", (1, 1), "white")

        self.assertEqual((0, 255), ImageColor.getcolor("black", "LA"))
        self.assertEqual((255, 255), ImageColor.getcolor("white", "LA"))
        self.assertEqual(
            (162, 33), ImageColor.getcolor("rgba(0, 255, 115, 33)", "LA"))
        Image.new("LA", (1, 1), "white")


if __name__ == '__main__':
    unittest.main()

# End of file
