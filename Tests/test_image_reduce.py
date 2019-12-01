from PIL import Image, ImageMode, ImageMath

from .helper import PillowTestCase, hopper, convert_to_comparable


class TestImageReduce(PillowTestCase):
    # There are several internal implementations
    remarkable_factors = [
        1, 2, 3, 4, 5, 6,  # special implementations
        (1, 2), (1, 3), (1, 4),  # 1xN implementation
        (2, 1), (3, 1), (4, 1),  # Nx1 implementation
        # general implementation with different paths
        (4, 6), (5, 6), (4, 7), (5, 7), (19, 17),
    ]

    @classmethod
    def setUpClass(cls):
        cls.gradients_image = Image.open("Tests/images/radial_gradients.png")
        cls.gradients_image.load()

    def test_args(self):
        im = Image.new("L", (10, 10))
        
        self.assertEqual((4, 4), im.reduce(3).size)
        self.assertEqual((4, 10), im.reduce((3, 1)).size)
        self.assertEqual((10, 4), im.reduce((1, 3)).size)

        with self.assertRaises(ValueError):
            im.reduce(0)
        with self.assertRaises(TypeError):
            im.reduce(2.0)
        with self.assertRaises(ValueError):
            im.reduce((0, 10))

    def get_image(self, mode):
        bands = [self.gradients_image]
        for _ in ImageMode.getmode(mode).bands[1:]:
            # rotate previous image
            band = bands[-1].transpose(Image.ROTATE_90)
            bands.append(band)
        # Correct alpha channel to exclude completely transparent pixels.
        # Low alpha values also emphasize error after alpha multiplication.
        if mode.endswith('A'):
            bands[-1] = bands[-1].point(lambda x: int(85 + x / 1.5))
        return Image.merge(mode, bands)

    def compare_reduce_with_reference(self, im, factor, average_diff=0.4, max_diff=1):
        """Image.reduce() should look very similar to Image.resize(BOX).

        A reference image is compiled from a large source area
        and possible last column and last row.
        +-----------+
        |..........c|
        |..........c|
        |..........c|
        |rrrrrrrrrrp|
        +-----------+
        """
        reduced = im.reduce(factor)

        if not isinstance(factor, (list, tuple)):
            factor = (factor, factor)

        reference = Image.new(im.mode, reduced.size)
        area_size = (im.size[0] // factor[0], im.size[1] // factor[1])
        area_box = (0, 0, area_size[0] * factor[0], area_size[1] * factor[1])
        area = im.resize(area_size, Image.BOX, area_box)
        reference.paste(area, (0, 0))

        if area_size[0] < reduced.size[0]:
            self.assertEqual(reduced.size[0] - area_size[0], 1)
            last_column_box = (area_box[2], 0, im.size[0], area_box[3])
            last_column = im.resize((1, area_size[1]), Image.BOX, last_column_box)
            reference.paste(last_column, (area_size[0], 0))

        if area_size[1] < reduced.size[1]:
            self.assertEqual(reduced.size[1] - area_size[1], 1)
            last_row_box = (0, area_box[3], area_box[2], im.size[1])
            last_row = im.resize((area_size[0], 1), Image.BOX, last_row_box)
            reference.paste(last_row, (0, area_size[1]))

        if area_size[0] < reduced.size[0] and area_size[1] < reduced.size[1]:
            last_pixel_box = (area_box[2], area_box[3], im.size[0], im.size[1])
            last_pixel = im.resize((1, 1), Image.BOX, last_pixel_box)
            reference.paste(last_pixel, area_size)

        try:
            self.assert_compare_images(reduced, reference, average_diff, max_diff)
        except Exception:
            reduced.save("_out.{}.{}x{}.reduced.png".format(im.mode, *factor))
            reference.save("_out.{}.{}x{}.reference.png".format(im.mode, *factor))
            raise

    def assert_compare_images(self, a, b, max_average_diff, max_diff=255):
        self.assertEqual(
            a.mode, b.mode, "got mode %r, expected %r" % (a.mode, b.mode))
        self.assertEqual(
            a.size, b.size, "got size %r, expected %r" % (a.size, b.size))

        a, b = convert_to_comparable(a, b)

        bands = ImageMode.getmode(a.mode).bands
        for band, ach, bch in zip(bands, a.split(), b.split()):
            ch_diff = ImageMath.eval("convert(abs(a - b), 'L')", a=ach, b=bch)
            ch_hist = ch_diff.histogram()

            average_diff = (sum(i * num for i, num in enumerate(ch_hist))
                            / float(a.size[0] * a.size[1]))
            self.assertGreaterEqual(
                max_average_diff, average_diff,
                ("average pixel value difference {:.4f} > expected {:.4f} "
                 "for '{}' band").format(average_diff, max_average_diff, band),
            )

            last_diff = [i for i, num in enumerate(ch_hist) if num > 0][-1]
            self.assertGreaterEqual(
                max_diff, last_diff,
                "max pixel value difference {} > expected {} for '{}' band"
                    .format(last_diff, max_diff, band),
            )

    def test_mode_L(self):
        im = self.get_image("L")
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor)

    def test_mode_LA(self):
        im = self.get_image("LA")
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor, 0.8, 5)
        
        # With opaque alpha, error should be way smaller
        im.putalpha(Image.new('L', im.size, 255))
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor)

    def test_mode_La(self):
        im = self.get_image("La")
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor)

    def test_mode_RGB(self):
        im = self.get_image("RGB")
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor)

    def test_mode_RGBA(self):
        im = self.get_image("RGBA")
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor, 0.8, 5)

        # With opaque alpha, error should be way smaller
        im.putalpha(Image.new('L', im.size, 255))
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor)

    def test_mode_RGBa(self):
        im = self.get_image("RGBa")
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor)

    def test_mode_CMYK(self):
        im = self.get_image("CMYK")
        for factor in self.remarkable_factors:
            self.compare_reduce_with_reference(im, factor)
