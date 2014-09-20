from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ImageFilter


class TestImageFilter(PillowTestCase):

    def test_sanity(self):

        def filter(filter):
            im = hopper("L")
            out = im.filter(filter)
            self.assertEqual(out.mode, im.mode)
            self.assertEqual(out.size, im.size)

        filter(ImageFilter.BLUR)
        filter(ImageFilter.CONTOUR)
        filter(ImageFilter.DETAIL)
        filter(ImageFilter.EDGE_ENHANCE)
        filter(ImageFilter.EDGE_ENHANCE_MORE)
        filter(ImageFilter.EMBOSS)
        filter(ImageFilter.FIND_EDGES)
        filter(ImageFilter.SMOOTH)
        filter(ImageFilter.SMOOTH_MORE)
        filter(ImageFilter.SHARPEN)
        filter(ImageFilter.MaxFilter)
        filter(ImageFilter.MedianFilter)
        filter(ImageFilter.MinFilter)
        filter(ImageFilter.ModeFilter)
        filter(ImageFilter.Kernel((3, 3), list(range(9))))
        filter(ImageFilter.GaussianBlur)
        filter(ImageFilter.GaussianBlur(5))
        filter(ImageFilter.UnsharpMask)
        filter(ImageFilter.UnsharpMask(10))

        self.assertRaises(TypeError, lambda: filter("hello"))

    def test_crash(self):

        # crashes on small images
        im = Image.new("RGB", (1, 1))
        im.filter(ImageFilter.SMOOTH)

        im = Image.new("RGB", (2, 2))
        im.filter(ImageFilter.SMOOTH)

        im = Image.new("RGB", (3, 3))
        im.filter(ImageFilter.SMOOTH)

    def test_modefilter(self):

        def modefilter(mode):
            im = Image.new(mode, (3, 3), None)
            im.putdata(list(range(9)))
            # image is:
            #   0 1 2
            #   3 4 5
            #   6 7 8
            mod = im.filter(ImageFilter.ModeFilter).getpixel((1, 1))
            im.putdata([0, 0, 1, 2, 5, 1, 5, 2, 0])  # mode=0
            mod2 = im.filter(ImageFilter.ModeFilter).getpixel((1, 1))
            return mod, mod2

        self.assertEqual(modefilter("1"), (4, 0))
        self.assertEqual(modefilter("L"), (4, 0))
        self.assertEqual(modefilter("P"), (4, 0))
        self.assertEqual(modefilter("RGB"), ((4, 0, 0), (0, 0, 0)))

    def test_rankfilter(self):

        def rankfilter(mode):
            im = Image.new(mode, (3, 3), None)
            im.putdata(list(range(9)))
            # image is:
            #   0 1 2
            #   3 4 5
            #   6 7 8
            min = im.filter(ImageFilter.MinFilter).getpixel((1, 1))
            med = im.filter(ImageFilter.MedianFilter).getpixel((1, 1))
            max = im.filter(ImageFilter.MaxFilter).getpixel((1, 1))
            return min, med, max

        self.assertEqual(rankfilter("1"), (0, 4, 8))
        self.assertEqual(rankfilter("L"), (0, 4, 8))
        self.assertRaises(ValueError, lambda: rankfilter("P"))
        self.assertEqual(rankfilter("RGB"), ((0, 0, 0), (4, 0, 0), (8, 0, 0)))
        self.assertEqual(rankfilter("I"), (0, 4, 8))
        self.assertEqual(rankfilter("F"), (0.0, 4.0, 8.0))


if __name__ == '__main__':
    unittest.main()

# End of file
