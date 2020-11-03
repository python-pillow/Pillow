import pytest

from PIL import Image, ImageFilter

from .helper import assert_image_equal, hopper


def test_sanity():
    def apply_filter(filter_to_apply):
        for mode in ["L", "RGB", "CMYK"]:
            im = hopper(mode)
            out = im.filter(filter_to_apply)
            assert out.mode == im.mode
            assert out.size == im.size

    apply_filter(ImageFilter.BLUR)
    apply_filter(ImageFilter.CONTOUR)
    apply_filter(ImageFilter.DETAIL)
    apply_filter(ImageFilter.EDGE_ENHANCE)
    apply_filter(ImageFilter.EDGE_ENHANCE_MORE)
    apply_filter(ImageFilter.EMBOSS)
    apply_filter(ImageFilter.FIND_EDGES)
    apply_filter(ImageFilter.SMOOTH)
    apply_filter(ImageFilter.SMOOTH_MORE)
    apply_filter(ImageFilter.SHARPEN)
    apply_filter(ImageFilter.MaxFilter)
    apply_filter(ImageFilter.MedianFilter)
    apply_filter(ImageFilter.MinFilter)
    apply_filter(ImageFilter.ModeFilter)
    apply_filter(ImageFilter.GaussianBlur)
    apply_filter(ImageFilter.GaussianBlur(5))
    apply_filter(ImageFilter.BoxBlur(5))
    apply_filter(ImageFilter.UnsharpMask)
    apply_filter(ImageFilter.UnsharpMask(10))

    with pytest.raises(TypeError):
        apply_filter("hello")


def test_crash():

    # crashes on small images
    im = Image.new("RGB", (1, 1))
    im.filter(ImageFilter.SMOOTH)

    im = Image.new("RGB", (2, 2))
    im.filter(ImageFilter.SMOOTH)

    im = Image.new("RGB", (3, 3))
    im.filter(ImageFilter.SMOOTH)


def test_modefilter():
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

    assert modefilter("1") == (4, 0)
    assert modefilter("L") == (4, 0)
    assert modefilter("P") == (4, 0)
    assert modefilter("RGB") == ((4, 0, 0), (0, 0, 0))


def test_rankfilter():
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

    assert rankfilter("1") == (0, 4, 8)
    assert rankfilter("L") == (0, 4, 8)
    with pytest.raises(ValueError):
        rankfilter("P")
    assert rankfilter("RGB") == ((0, 0, 0), (4, 0, 0), (8, 0, 0))
    assert rankfilter("I") == (0, 4, 8)
    assert rankfilter("F") == (0.0, 4.0, 8.0)


def test_rankfilter_properties():
    rankfilter = ImageFilter.RankFilter(1, 2)

    assert rankfilter.size == 1
    assert rankfilter.rank == 2


def test_builtinfilter_p():
    builtinFilter = ImageFilter.BuiltinFilter()

    with pytest.raises(ValueError):
        builtinFilter.filter(hopper("P"))


def test_kernel_not_enough_coefficients():
    with pytest.raises(ValueError):
        ImageFilter.Kernel((3, 3), (0, 0))


def test_consistency_3x3():
    with Image.open("Tests/images/hopper.bmp") as source:
        with Image.open("Tests/images/hopper_emboss.bmp") as reference:
            kernel = ImageFilter.Kernel(
                (3, 3),
                # fmt: off
                (-1, -1,  0,
                 -1,  0,  1,
                 0,   1,  1),
                # fmt: on
                0.3,
            )
            source = source.split() * 2
            reference = reference.split() * 2

            for mode in ["L", "LA", "RGB", "CMYK"]:
                assert_image_equal(
                    Image.merge(mode, source[: len(mode)]).filter(kernel),
                    Image.merge(mode, reference[: len(mode)]),
                )


def test_consistency_5x5():
    with Image.open("Tests/images/hopper.bmp") as source:
        with Image.open("Tests/images/hopper_emboss_more.bmp") as reference:
            kernel = ImageFilter.Kernel(
                (5, 5),
                # fmt: off
                (-1, -1, -1, -1,  0,
                 -1, -1, -1,  0,  1,
                 -1, -1,  0,  1,  1,
                 -1,  0,  1,  1,  1,
                 0,   1,  1,  1,  1),
                # fmt: on
                0.3,
            )
            source = source.split() * 2
            reference = reference.split() * 2

            for mode in ["L", "LA", "RGB", "CMYK"]:
                assert_image_equal(
                    Image.merge(mode, source[: len(mode)]).filter(kernel),
                    Image.merge(mode, reference[: len(mode)]),
                )
