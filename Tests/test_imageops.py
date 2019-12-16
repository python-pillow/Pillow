from PIL import Image, ImageOps

from .helper import PillowTestCase, hopper

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


class TestImageOps(PillowTestCase):
    class Deformer:
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

        ImageOps.pad(hopper("L"), (128, 128))
        ImageOps.pad(hopper("RGB"), (128, 128))

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

        ImageOps.exif_transpose(hopper("L"))
        ImageOps.exif_transpose(hopper("RGB"))

    def test_1pxfit(self):
        # Division by zero in equalize if image is 1 pixel high
        newimg = ImageOps.fit(hopper("RGB").resize((1, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((1, 100)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((100, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

    def test_fit_same_ratio(self):
        # The ratio for this image is 1000.0 / 755 = 1.3245033112582782
        # If the ratios are not acknowledged to be the same,
        # and Pillow attempts to adjust the width to
        # 1.3245033112582782 * 755 = 1000.0000000000001
        # then centering this greater width causes a negative x offset when cropping
        with Image.new("RGB", (1000, 755)) as im:
            new_im = ImageOps.fit(im, (1000, 755))
            self.assertEqual(new_im.size, (1000, 755))

    def test_pad(self):
        # Same ratio
        im = hopper()
        new_size = (im.width * 2, im.height * 2)
        new_im = ImageOps.pad(im, new_size)
        self.assertEqual(new_im.size, new_size)

        for label, color, new_size in [
            ("h", None, (im.width * 4, im.height * 2)),
            ("v", "#f00", (im.width * 2, im.height * 4)),
        ]:
            for i, centering in enumerate([(0, 0), (0.5, 0.5), (1, 1)]):
                new_im = ImageOps.pad(im, new_size, color=color, centering=centering)
                self.assertEqual(new_im.size, new_size)

                with Image.open(
                    "Tests/images/imageops_pad_" + label + "_" + str(i) + ".jpg"
                ) as target:
                    self.assert_image_similar(new_im, target, 6)

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

    def test_colorize_2color(self):
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
        self.assert_tuple_approx_equal(
            im_test.getpixel(left),
            (255, 0, 0),
            threshold=1,
            msg="black test pixel incorrect",
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(middle),
            (127, 63, 0),
            threshold=1,
            msg="mid test pixel incorrect",
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(right),
            (0, 127, 0),
            threshold=1,
            msg="white test pixel incorrect",
        )

    def test_colorize_2color_offset(self):
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
        self.assert_tuple_approx_equal(
            im_test.getpixel(left),
            (255, 0, 0),
            threshold=1,
            msg="black test pixel incorrect",
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(middle),
            (127, 63, 0),
            threshold=1,
            msg="mid test pixel incorrect",
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(right),
            (0, 127, 0),
            threshold=1,
            msg="white test pixel incorrect",
        )

    def test_colorize_3color_offset(self):
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
        self.assert_tuple_approx_equal(
            im_test.getpixel(left),
            (255, 0, 0),
            threshold=1,
            msg="black test pixel incorrect",
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(left_middle),
            (127, 0, 127),
            threshold=1,
            msg="low-mid test pixel incorrect",
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(middle), (0, 0, 255), threshold=1, msg="mid incorrect"
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(right_middle),
            (0, 63, 127),
            threshold=1,
            msg="high-mid test pixel incorrect",
        )
        self.assert_tuple_approx_equal(
            im_test.getpixel(right),
            (0, 127, 0),
            threshold=1,
            msg="white test pixel incorrect",
        )

    def test_exif_transpose(self):
        exts = [".jpg"]
        if HAVE_WEBP and _webp.HAVE_WEBPANIM:
            exts.append(".webp")
        for ext in exts:
            with Image.open("Tests/images/hopper" + ext) as base_im:

                def check(orientation_im):
                    for im in [
                        orientation_im,
                        orientation_im.copy(),
                    ]:  # ImageFile  # Image
                        if orientation_im is base_im:
                            self.assertNotIn("exif", im.info)
                        else:
                            original_exif = im.info["exif"]
                        transposed_im = ImageOps.exif_transpose(im)
                        self.assert_image_similar(base_im, transposed_im, 17)
                        if orientation_im is base_im:
                            self.assertNotIn("exif", im.info)
                        else:
                            self.assertNotEqual(
                                transposed_im.info["exif"], original_exif
                            )

                            self.assertNotIn(0x0112, transposed_im.getexif())

                        # Repeat the operation
                        # to test that it does not keep transposing
                        transposed_im2 = ImageOps.exif_transpose(transposed_im)
                        self.assert_image_equal(transposed_im2, transposed_im)

                check(base_im)
                for i in range(2, 9):
                    with Image.open(
                        "Tests/images/hopper_orientation_" + str(i) + ext
                    ) as orientation_im:
                        check(orientation_im)
