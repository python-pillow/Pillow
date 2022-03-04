import pytest

from PIL import Image, ImageDraw, ImageOps, ImageStat, features

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    assert_tuple_approx_equal,
    hopper,
)


class Deformer:
    def getmesh(self, im):
        x, y = im.size
        return [((0, 0, x, y), (0, 0, x, 0, x, y, y, 0))]


deformer = Deformer()


def test_sanity():

    ImageOps.autocontrast(hopper("L"))
    ImageOps.autocontrast(hopper("RGB"))

    ImageOps.autocontrast(hopper("L"), cutoff=10)
    ImageOps.autocontrast(hopper("L"), cutoff=(2, 10))
    ImageOps.autocontrast(hopper("L"), ignore=[0, 255])
    ImageOps.autocontrast(hopper("L"), mask=hopper("L"))
    ImageOps.autocontrast(hopper("L"), preserve_tone=True)

    ImageOps.colorize(hopper("L"), (0, 0, 0), (255, 255, 255))
    ImageOps.colorize(hopper("L"), "black", "white")

    ImageOps.pad(hopper("L"), (128, 128))
    ImageOps.pad(hopper("RGB"), (128, 128))

    ImageOps.contain(hopper("L"), (128, 128))
    ImageOps.contain(hopper("RGB"), (128, 128))

    ImageOps.crop(hopper("L"), 1)
    ImageOps.crop(hopper("RGB"), 1)

    ImageOps.deform(hopper("L"), deformer)
    ImageOps.deform(hopper("RGB"), deformer)

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

    ImageOps.exif_transpose(hopper("L"))
    ImageOps.exif_transpose(hopper("RGB"))


def test_1pxfit():
    # Division by zero in equalize if image is 1 pixel high
    newimg = ImageOps.fit(hopper("RGB").resize((1, 1)), (35, 35))
    assert newimg.size == (35, 35)

    newimg = ImageOps.fit(hopper("RGB").resize((1, 100)), (35, 35))
    assert newimg.size == (35, 35)

    newimg = ImageOps.fit(hopper("RGB").resize((100, 1)), (35, 35))
    assert newimg.size == (35, 35)


def test_fit_same_ratio():
    # The ratio for this image is 1000.0 / 755 = 1.3245033112582782
    # If the ratios are not acknowledged to be the same,
    # and Pillow attempts to adjust the width to
    # 1.3245033112582782 * 755 = 1000.0000000000001
    # then centering this greater width causes a negative x offset when cropping
    with Image.new("RGB", (1000, 755)) as im:
        new_im = ImageOps.fit(im, (1000, 755))
        assert new_im.size == (1000, 755)


@pytest.mark.parametrize("new_size", ((256, 256), (512, 256), (256, 512)))
def test_contain(new_size):
    im = hopper()
    new_im = ImageOps.contain(im, new_size)
    assert new_im.size == (256, 256)


def test_pad():
    # Same ratio
    im = hopper()
    new_size = (im.width * 2, im.height * 2)
    new_im = ImageOps.pad(im, new_size)
    assert new_im.size == new_size

    for label, color, new_size in [
        ("h", None, (im.width * 4, im.height * 2)),
        ("v", "#f00", (im.width * 2, im.height * 4)),
    ]:
        for i, centering in enumerate([(0, 0), (0.5, 0.5), (1, 1)]):
            new_im = ImageOps.pad(im, new_size, color=color, centering=centering)
            assert new_im.size == new_size

            assert_image_similar_tofile(
                new_im, "Tests/images/imageops_pad_" + label + "_" + str(i) + ".jpg", 6
            )


def test_pil163():
    # Division by zero in equalize if < 255 pixels in image (@PIL163)

    i = hopper("RGB").resize((15, 16))

    ImageOps.equalize(i.convert("L"))
    ImageOps.equalize(i.convert("P"))
    ImageOps.equalize(i.convert("RGB"))


def test_scale():
    # Test the scaling function
    i = hopper("L").resize((50, 50))

    with pytest.raises(ValueError):
        ImageOps.scale(i, -1)

    newimg = ImageOps.scale(i, 1)
    assert newimg.size == (50, 50)

    newimg = ImageOps.scale(i, 2)
    assert newimg.size == (100, 100)

    newimg = ImageOps.scale(i, 0.5)
    assert newimg.size == (25, 25)


@pytest.mark.parametrize("border", (10, (1, 2, 3, 4)))
def test_expand_palette(border):
    with Image.open("Tests/images/p_16.tga") as im:
        im_expanded = ImageOps.expand(im, border, (255, 0, 0))

        if isinstance(border, int):
            left = top = right = bottom = border
        else:
            left, top, right, bottom = border
        px = im_expanded.convert("RGB").load()
        for x in range(im_expanded.width):
            for b in range(top):
                assert px[x, b] == (255, 0, 0)
            for b in range(bottom):
                assert px[x, im_expanded.height - 1 - b] == (255, 0, 0)
        for y in range(im_expanded.height):
            for b in range(left):
                assert px[b, y] == (255, 0, 0)
            for b in range(right):
                assert px[im_expanded.width - 1 - b, y] == (255, 0, 0)

        im_cropped = im_expanded.crop(
            (left, top, im_expanded.width - right, im_expanded.height - bottom)
        )
        assert_image_equal(im_cropped, im)


def test_colorize_2color():
    # Test the colorizing function with 2-color functionality

    # Open test image (256px by 10px, black to white)
    with Image.open("Tests/images/bw_gradient.png") as im:
        im = im.convert("L")

    # Create image with original 2-color functionality
    im_test = ImageOps.colorize(im, "red", "green")

    # Test output image (2-color)
    left = (0, 1)
    middle = (127, 1)
    right = (255, 1)
    assert_tuple_approx_equal(
        im_test.getpixel(left),
        (255, 0, 0),
        threshold=1,
        msg="black test pixel incorrect",
    )
    assert_tuple_approx_equal(
        im_test.getpixel(middle),
        (127, 63, 0),
        threshold=1,
        msg="mid test pixel incorrect",
    )
    assert_tuple_approx_equal(
        im_test.getpixel(right),
        (0, 127, 0),
        threshold=1,
        msg="white test pixel incorrect",
    )


def test_colorize_2color_offset():
    # Test the colorizing function with 2-color functionality and offset

    # Open test image (256px by 10px, black to white)
    with Image.open("Tests/images/bw_gradient.png") as im:
        im = im.convert("L")

    # Create image with original 2-color functionality with offsets
    im_test = ImageOps.colorize(
        im, black="red", white="green", blackpoint=50, whitepoint=100
    )

    # Test output image (2-color) with offsets
    left = (25, 1)
    middle = (75, 1)
    right = (125, 1)
    assert_tuple_approx_equal(
        im_test.getpixel(left),
        (255, 0, 0),
        threshold=1,
        msg="black test pixel incorrect",
    )
    assert_tuple_approx_equal(
        im_test.getpixel(middle),
        (127, 63, 0),
        threshold=1,
        msg="mid test pixel incorrect",
    )
    assert_tuple_approx_equal(
        im_test.getpixel(right),
        (0, 127, 0),
        threshold=1,
        msg="white test pixel incorrect",
    )


def test_colorize_3color_offset():
    # Test the colorizing function with 3-color functionality and offset

    # Open test image (256px by 10px, black to white)
    with Image.open("Tests/images/bw_gradient.png") as im:
        im = im.convert("L")

    # Create image with new three color functionality with offsets
    im_test = ImageOps.colorize(
        im,
        black="red",
        white="green",
        mid="blue",
        blackpoint=50,
        whitepoint=200,
        midpoint=100,
    )

    # Test output image (3-color) with offsets
    left = (25, 1)
    left_middle = (75, 1)
    middle = (100, 1)
    right_middle = (150, 1)
    right = (225, 1)
    assert_tuple_approx_equal(
        im_test.getpixel(left),
        (255, 0, 0),
        threshold=1,
        msg="black test pixel incorrect",
    )
    assert_tuple_approx_equal(
        im_test.getpixel(left_middle),
        (127, 0, 127),
        threshold=1,
        msg="low-mid test pixel incorrect",
    )
    assert_tuple_approx_equal(
        im_test.getpixel(middle), (0, 0, 255), threshold=1, msg="mid incorrect"
    )
    assert_tuple_approx_equal(
        im_test.getpixel(right_middle),
        (0, 63, 127),
        threshold=1,
        msg="high-mid test pixel incorrect",
    )
    assert_tuple_approx_equal(
        im_test.getpixel(right),
        (0, 127, 0),
        threshold=1,
        msg="white test pixel incorrect",
    )


def test_exif_transpose():
    exts = [".jpg"]
    if features.check("webp") and features.check("webp_anim"):
        exts.append(".webp")
    for ext in exts:
        with Image.open("Tests/images/hopper" + ext) as base_im:

            def check(orientation_im):
                for im in [
                    orientation_im,
                    orientation_im.copy(),
                ]:  # ImageFile  # Image
                    if orientation_im is base_im:
                        assert "exif" not in im.info
                    else:
                        original_exif = im.info["exif"]
                    transposed_im = ImageOps.exif_transpose(im)
                    assert_image_similar(base_im, transposed_im, 17)
                    if orientation_im is base_im:
                        assert "exif" not in im.info
                    else:
                        assert transposed_im.info["exif"] != original_exif

                        assert 0x0112 in im.getexif()
                        assert 0x0112 not in transposed_im.getexif()

                    # Repeat the operation to test that it does not keep transposing
                    transposed_im2 = ImageOps.exif_transpose(transposed_im)
                    assert_image_equal(transposed_im2, transposed_im)

            check(base_im)
            for i in range(2, 9):
                with Image.open(
                    "Tests/images/hopper_orientation_" + str(i) + ext
                ) as orientation_im:
                    check(orientation_im)

    # Orientation from "XML:com.adobe.xmp" info key
    with Image.open("Tests/images/xmp_tags_orientation.png") as im:
        assert im.getexif()[0x0112] == 3

        transposed_im = ImageOps.exif_transpose(im)
        assert 0x0112 not in transposed_im.getexif()

    # Orientation from "Raw profile type exif" info key
    # This test image has been manually hexedited from exif_imagemagick.png
    # to have a different orientation
    with Image.open("Tests/images/exif_imagemagick_orientation.png") as im:
        assert im.getexif()[0x0112] == 3

        transposed_im = ImageOps.exif_transpose(im)
        assert 0x0112 not in transposed_im.getexif()

    # Orientation set directly on Image.Exif
    im = hopper()
    im.getexif()[0x0112] = 3
    transposed_im = ImageOps.exif_transpose(im)
    assert 0x0112 not in transposed_im.getexif()


def test_autocontrast_cutoff():
    # Test the cutoff argument of autocontrast
    with Image.open("Tests/images/bw_gradient.png") as img:

        def autocontrast(cutoff):
            return ImageOps.autocontrast(img, cutoff).histogram()

        assert autocontrast(10) == autocontrast((10, 10))
        assert autocontrast(10) != autocontrast((1, 10))


def test_autocontrast_mask_toy_input():
    # Test the mask argument of autocontrast
    with Image.open("Tests/images/bw_gradient.png") as img:

        rect_mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(rect_mask)
        x0 = img.size[0] // 4
        y0 = img.size[1] // 4
        x1 = 3 * img.size[0] // 4
        y1 = 3 * img.size[1] // 4
        draw.rectangle((x0, y0, x1, y1), fill=255)

        result = ImageOps.autocontrast(img, mask=rect_mask)
        result_nomask = ImageOps.autocontrast(img)

        assert result != result_nomask
        assert ImageStat.Stat(result, mask=rect_mask).median == [127]
        assert ImageStat.Stat(result_nomask).median == [128]


def test_autocontrast_mask_real_input():
    # Test the autocontrast with a rectangular mask
    with Image.open("Tests/images/iptc.jpg") as img:

        rect_mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(rect_mask)
        x0, y0 = img.size[0] // 2, img.size[1] // 2
        x1, y1 = img.size[0] - 40, img.size[1]
        draw.rectangle((x0, y0, x1, y1), fill=255)

        result = ImageOps.autocontrast(img, mask=rect_mask)
        result_nomask = ImageOps.autocontrast(img)

        assert result_nomask != result
        assert_tuple_approx_equal(
            ImageStat.Stat(result, mask=rect_mask).median,
            [195, 202, 184],
            threshold=2,
            msg="autocontrast with mask pixel incorrect",
        )
        assert_tuple_approx_equal(
            ImageStat.Stat(result_nomask).median,
            [119, 106, 79],
            threshold=2,
            msg="autocontrast without mask pixel incorrect",
        )


def test_autocontrast_preserve_tone():
    def autocontrast(mode, preserve_tone):
        im = hopper(mode)
        return ImageOps.autocontrast(im, preserve_tone=preserve_tone).histogram()

    assert autocontrast("RGB", True) != autocontrast("RGB", False)
    assert autocontrast("L", True) == autocontrast("L", False)


def test_autocontrast_preserve_gradient():
    gradient = Image.linear_gradient("L")

    # test with a grayscale gradient that extends to 0,255.
    # Should be a noop.
    out = ImageOps.autocontrast(gradient, cutoff=0, preserve_tone=True)

    assert_image_equal(gradient, out)

    # cutoff the top and bottom
    # autocontrast should make the first and last histogram entries equal
    # and, with rounding, should be 10% of the image pixels
    out = ImageOps.autocontrast(gradient, cutoff=10, preserve_tone=True)
    hist = out.histogram()
    assert hist[0] == hist[-1]
    assert hist[-1] == 256 * round(256 * 0.10)

    # in rgb
    img = gradient.convert("RGB")
    out = ImageOps.autocontrast(img, cutoff=0, preserve_tone=True)
    assert_image_equal(img, out)


@pytest.mark.parametrize(
    "color", ((255, 255, 255), (127, 255, 0), (127, 127, 127), (0, 0, 0))
)
def test_autocontrast_preserve_one_color(color):
    img = Image.new("RGB", (10, 10), color)

    # single color images shouldn't change
    out = ImageOps.autocontrast(img, cutoff=0, preserve_tone=True)
    assert_image_equal(img, out)  # single color, no cutoff

    # even if there is a cutoff
    out = ImageOps.autocontrast(
        img, cutoff=10, preserve_tone=True
    )  # single color 10 cutoff
    assert_image_equal(img, out)
