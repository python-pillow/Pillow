from helper import unittest, PillowTestCase

from PIL import Image
from PIL import ImageColor


class TestImageColor(PillowTestCase):

    def test_hash(self):
        # short 3 components
        self.assertEqual((255, 0, 0), ImageColor.getrgb("#f00"))
        self.assertEqual((0, 255, 0), ImageColor.getrgb("#0f0"))
        self.assertEqual((0, 0, 255), ImageColor.getrgb("#00f"))

        # short 4 components
        self.assertEqual((255, 0, 0, 0), ImageColor.getrgb("#f000"))
        self.assertEqual((0, 255, 0, 0), ImageColor.getrgb("#0f00"))
        self.assertEqual((0, 0, 255, 0), ImageColor.getrgb("#00f0"))
        self.assertEqual((0, 0, 0, 255), ImageColor.getrgb("#000f"))

        # long 3 components
        self.assertEqual((222, 0, 0), ImageColor.getrgb("#de0000"))
        self.assertEqual((0, 222, 0), ImageColor.getrgb("#00de00"))
        self.assertEqual((0, 0, 222), ImageColor.getrgb("#0000de"))

        # long 4 components
        self.assertEqual((222, 0, 0, 0), ImageColor.getrgb("#de000000"))
        self.assertEqual((0, 222, 0, 0), ImageColor.getrgb("#00de0000"))
        self.assertEqual((0, 0, 222, 0), ImageColor.getrgb("#0000de00"))
        self.assertEqual((0, 0, 0, 222), ImageColor.getrgb("#000000de"))

        # case insensitivity
        self.assertEqual(ImageColor.getrgb("#DEF"), ImageColor.getrgb("#def"))
        self.assertEqual(ImageColor.getrgb("#CDEF"), ImageColor.getrgb("#cdef"))
        self.assertEqual(ImageColor.getrgb("#DEFDEF"),
                         ImageColor.getrgb("#defdef"))
        self.assertEqual(ImageColor.getrgb("#CDEFCDEF"),
                         ImageColor.getrgb("#cdefcdef"))

        # not a number
        self.assertRaises(ValueError, ImageColor.getrgb, "#fo0")
        self.assertRaises(ValueError, ImageColor.getrgb, "#fo00")
        self.assertRaises(ValueError, ImageColor.getrgb, "#fo0000")
        self.assertRaises(ValueError, ImageColor.getrgb, "#fo000000")

        # wrong number of components
        self.assertRaises(ValueError, ImageColor.getrgb, "#f0000")
        self.assertRaises(ValueError, ImageColor.getrgb, "#f000000")
        self.assertRaises(ValueError, ImageColor.getrgb, "#f00000000")
        self.assertRaises(ValueError, ImageColor.getrgb, "#f000000000")
        self.assertRaises(ValueError, ImageColor.getrgb, "#f00000 ")

    def test_colormap(self):
        self.assertEqual((0, 0, 0), ImageColor.getrgb("black"))
        self.assertEqual((255, 255, 255), ImageColor.getrgb("white"))
        self.assertEqual((255, 255, 255), ImageColor.getrgb("WHITE"))

        self.assertRaises(ValueError, ImageColor.getrgb, "black ")

    def test_functions(self):
        # rgb numbers
        self.assertEqual((255, 0, 0), ImageColor.getrgb("rgb(255,0,0)"))
        self.assertEqual((0, 255, 0), ImageColor.getrgb("rgb(0,255,0)"))
        self.assertEqual((0, 0, 255), ImageColor.getrgb("rgb(0,0,255)"))

        # percents
        self.assertEqual((255, 0, 0), ImageColor.getrgb("rgb(100%,0%,0%)"))
        self.assertEqual((0, 255, 0), ImageColor.getrgb("rgb(0%,100%,0%)"))
        self.assertEqual((0, 0, 255), ImageColor.getrgb("rgb(0%,0%,100%)"))

        # rgba numbers
        self.assertEqual((255, 0, 0, 0), ImageColor.getrgb("rgba(255,0,0,0)"))
        self.assertEqual((0, 255, 0, 0), ImageColor.getrgb("rgba(0,255,0,0)"))
        self.assertEqual((0, 0, 255, 0), ImageColor.getrgb("rgba(0,0,255,0)"))
        self.assertEqual((0, 0, 0, 255), ImageColor.getrgb("rgba(0,0,0,255)"))

        self.assertEqual((255, 0, 0), ImageColor.getrgb("hsl(0,100%,50%)"))
        self.assertEqual((255, 0, 0), ImageColor.getrgb("hsl(360,100%,50%)"))
        self.assertEqual((0, 255, 255), ImageColor.getrgb("hsl(180,100%,50%)"))

        # case insensitivity
        self.assertEqual(ImageColor.getrgb("RGB(255,0,0)"),
                         ImageColor.getrgb("rgb(255,0,0)"))
        self.assertEqual(ImageColor.getrgb("RGB(100%,0%,0%)"),
                         ImageColor.getrgb("rgb(100%,0%,0%)"))
        self.assertEqual(ImageColor.getrgb("RGBA(255,0,0,0)"),
                         ImageColor.getrgb("rgba(255,0,0,0)"))
        self.assertEqual(ImageColor.getrgb("HSL(0,100%,50%)"),
                         ImageColor.getrgb("hsl(0,100%,50%)"))

        # space agnosticism
        self.assertEqual((255, 0, 0),
                         ImageColor.getrgb("rgb(  255  ,  0  ,  0  )"))
        self.assertEqual((255, 0, 0),
                         ImageColor.getrgb("rgb(  100%  ,  0%  ,  0%  )"))
        self.assertEqual((255, 0, 0, 0),
                         ImageColor.getrgb("rgba(  255  ,  0  ,  0  ,  0  )"))
        self.assertEqual((255, 0, 0),
                         ImageColor.getrgb("hsl(  0  ,  100%  ,  50%  )"))

        # wrong number of components
        self.assertRaises(ValueError, ImageColor.getrgb, "rgb(255,0)")
        self.assertRaises(ValueError, ImageColor.getrgb, "rgb(255,0,0,0)")

        self.assertRaises(ValueError, ImageColor.getrgb, "rgb(100%,0%)")
        self.assertRaises(ValueError, ImageColor.getrgb, "rgb(100%,0%,0)")
        self.assertRaises(ValueError, ImageColor.getrgb, "rgb(100%,0%,0 %)")
        self.assertRaises(ValueError, ImageColor.getrgb, "rgb(100%,0%,0%,0%)")

        self.assertRaises(ValueError, ImageColor.getrgb, "rgba(255,0,0)")
        self.assertRaises(ValueError, ImageColor.getrgb, "rgba(255,0,0,0,0)")

        self.assertRaises(ValueError, ImageColor.getrgb, "hsl(0,100%)")
        self.assertRaises(ValueError, ImageColor.getrgb, "hsl(0,100%,0%,0%)")
        self.assertRaises(ValueError, ImageColor.getrgb, "hsl(0%,100%,50%)")
        self.assertRaises(ValueError, ImageColor.getrgb, "hsl(0,100,50%)")
        self.assertRaises(ValueError, ImageColor.getrgb, "hsl(0,100%,50)")

    # look for rounding errors (based on code by Tim Hatch)
    def test_rounding_errors(self):

        for color in list(ImageColor.colormap.keys()):
            expected = Image.new(
                "RGB", (1, 1), color).convert("L").getpixel((0, 0))
            actual = ImageColor.getcolor(color, 'L')
            self.assertEqual(expected, actual)

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
