from PIL import Image, ImageFilter

from .helper import PillowTestCase, hopper


class TestImageFilter(PillowTestCase):
    def test_sanity(self):
        def filter(filter):
            for mode in ["L", "RGB", "CMYK"]:
                im = hopper(mode)
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
        filter(ImageFilter.GaussianBlur)
        filter(ImageFilter.GaussianBlur(5))
        filter(ImageFilter.BoxBlur(5))
        filter(ImageFilter.UnsharpMask)
        filter(ImageFilter.UnsharpMask(10))

        self.assertRaises(TypeError, filter, "hello")

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
            minimum = im.filter(ImageFilter.MinFilter).getpixel((1, 1))
            med = im.filter(ImageFilter.MedianFilter).getpixel((1, 1))
            maximum = im.filter(ImageFilter.MaxFilter).getpixel((1, 1))
            return minimum, med, maximum

        self.assertEqual(rankfilter("1"), (0, 4, 8))
        self.assertEqual(rankfilter("L"), (0, 4, 8))
        self.assertRaises(ValueError, rankfilter, "P")
        self.assertEqual(rankfilter("RGB"), ((0, 0, 0), (4, 0, 0), (8, 0, 0)))
        self.assertEqual(rankfilter("I"), (0, 4, 8))
        self.assertEqual(rankfilter("F"), (0.0, 4.0, 8.0))

    def test_rankfilter_properties(self):
        rankfilter = ImageFilter.RankFilter(1, 2)

        self.assertEqual(rankfilter.size, 1)
        self.assertEqual(rankfilter.rank, 2)

    def test_builtinfilter_p(self):
        builtinFilter = ImageFilter.BuiltinFilter()

        self.assertRaises(ValueError, builtinFilter.filter, hopper("P"))

    def test_kernel_not_enough_coefficients(self):
        self.assertRaises(ValueError, lambda: ImageFilter.Kernel((3, 3), (0, 0)))

    def test_consistency_3x3(self):
        with Image.open("Tests/images/hopper.bmp") as source:
            with Image.open("Tests/images/hopper_emboss.bmp") as reference:
                kernel = ImageFilter.Kernel(  # noqa: E127
                    (3, 3),
                    # fmt: off
                    (-1, -1,  0,
                     -1,  0,  1,
                      0,  1,  1),
                    # fmt: on
                    0.3,
                )
                source = source.split() * 2
                reference = reference.split() * 2

                for mode in ["L", "LA", "RGB", "CMYK"]:
                    self.assert_image_equal(
                        Image.merge(mode, source[: len(mode)]).filter(kernel),
                        Image.merge(mode, reference[: len(mode)]),
                    )

    def test_consistency_5x5(self):
        with Image.open("Tests/images/hopper.bmp") as source:
            with Image.open("Tests/images/hopper_emboss_more.bmp") as reference:
                kernel = ImageFilter.Kernel(  # noqa: E127
                    (5, 5),
                    # fmt: off
                    (-1, -1, -1, -1,  0,
                     -1, -1, -1,  0,  1,
                     -1, -1,  0,  1,  1,
                     -1,  0,  1,  1,  1,
                      0,  1,  1,  1,  1),
                    # fmt: on
                    0.3,
                )
                source = source.split() * 2
                reference = reference.split() * 2

                for mode in ["L", "LA", "RGB", "CMYK"]:
                    self.assert_image_equal(
                        Image.merge(mode, source[: len(mode)]).filter(kernel),
                        Image.merge(mode, reference[: len(mode)]),
                    )
