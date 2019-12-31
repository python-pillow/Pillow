"""
Tests for resize functionality.
"""
from itertools import permutations

from PIL import Image

from .helper import PillowTestCase, hopper


class TestImagingCoreResize(PillowTestCase):
    def resize(self, im, size, f):
        # Image class independent version of resize.
        im.load()
        return im._new(im.im.resize(size, f))

    def test_nearest_mode(self):
        for mode in [
            "1",
            "P",
            "L",
            "I",
            "F",
            "RGB",
            "RGBA",
            "CMYK",
            "YCbCr",
            "I;16",
        ]:  # exotic mode
            im = hopper(mode)
            r = self.resize(im, (15, 12), Image.NEAREST)
            self.assertEqual(r.mode, mode)
            self.assertEqual(r.size, (15, 12))
            self.assertEqual(r.im.bands, im.im.bands)

    def test_convolution_modes(self):
        self.assertRaises(
            ValueError, self.resize, hopper("1"), (15, 12), Image.BILINEAR
        )
        self.assertRaises(
            ValueError, self.resize, hopper("P"), (15, 12), Image.BILINEAR
        )
        self.assertRaises(
            ValueError, self.resize, hopper("I;16"), (15, 12), Image.BILINEAR
        )
        for mode in ["L", "I", "F", "RGB", "RGBA", "CMYK", "YCbCr"]:
            im = hopper(mode)
            r = self.resize(im, (15, 12), Image.BILINEAR)
            self.assertEqual(r.mode, mode)
            self.assertEqual(r.size, (15, 12))
            self.assertEqual(r.im.bands, im.im.bands)

    def test_reduce_filters(self):
        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            r = self.resize(hopper("RGB"), (15, 12), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (15, 12))

    def test_enlarge_filters(self):
        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            r = self.resize(hopper("RGB"), (212, 195), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (212, 195))

    def test_endianness(self):
        # Make an image with one colored pixel, in one channel.
        # When resized, that channel should be the same as a GS image.
        # Other channels should be unaffected.
        # The R and A channels should not swap, which is indicative of
        # an endianness issues.

        samples = {
            "blank": Image.new("L", (2, 2), 0),
            "filled": Image.new("L", (2, 2), 255),
            "dirty": Image.new("L", (2, 2), 0),
        }
        samples["dirty"].putpixel((1, 1), 128)

        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            # samples resized with current filter
            references = {
                name: self.resize(ch, (4, 4), f) for name, ch in samples.items()
            }

            for mode, channels_set in [
                ("RGB", ("blank", "filled", "dirty")),
                ("RGBA", ("blank", "blank", "filled", "dirty")),
                ("LA", ("filled", "dirty")),
            ]:
                for channels in set(permutations(channels_set)):
                    # compile image from different channels permutations
                    im = Image.merge(mode, [samples[ch] for ch in channels])
                    resized = self.resize(im, (4, 4), f)

                    for i, ch in enumerate(resized.split()):
                        # check what resized channel in image is the same
                        # as separately resized channel
                        self.assert_image_equal(ch, references[channels[i]])

    def test_enlarge_zero(self):
        for f in [
            Image.NEAREST,
            Image.BOX,
            Image.BILINEAR,
            Image.HAMMING,
            Image.BICUBIC,
            Image.LANCZOS,
        ]:
            r = self.resize(Image.new("RGB", (0, 0), "white"), (212, 195), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (212, 195))
            self.assertEqual(r.getdata()[0], (0, 0, 0))

    def test_unknown_filter(self):
        self.assertRaises(ValueError, self.resize, hopper(), (10, 10), 9)


class TestReducingGapResize(PillowTestCase):
    @classmethod
    def setUpClass(cls):
        cls.gradients_image = Image.open("Tests/images/radial_gradients.png")
        cls.gradients_image.load()

    def test_reducing_gap_values(self):
        ref = self.gradients_image.resize((52, 34), Image.BICUBIC, reducing_gap=None)
        im = self.gradients_image.resize((52, 34), Image.BICUBIC)
        self.assert_image_equal(ref, im)

        with self.assertRaises(ValueError):
            self.gradients_image.resize((52, 34), Image.BICUBIC, reducing_gap=0)

        with self.assertRaises(ValueError):
            self.gradients_image.resize((52, 34), Image.BICUBIC, reducing_gap=0.99)

    def test_reducing_gap_1(self):
        for box, epsilon in [
            (None, 4),
            ((1.1, 2.2, 510.8, 510.9), 4),
            ((3, 10, 410, 256), 10),
        ]:
            ref = self.gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = self.gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=1.0
            )

            with self.assertRaises(AssertionError):
                self.assert_image_equal(ref, im)

            self.assert_image_similar(ref, im, epsilon)

    def test_reducing_gap_2(self):
        for box, epsilon in [
            (None, 1.5),
            ((1.1, 2.2, 510.8, 510.9), 1.5),
            ((3, 10, 410, 256), 1),
        ]:
            ref = self.gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = self.gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=2.0
            )

            with self.assertRaises(AssertionError):
                self.assert_image_equal(ref, im)

            self.assert_image_similar(ref, im, epsilon)

    def test_reducing_gap_3(self):
        for box, epsilon in [
            (None, 1),
            ((1.1, 2.2, 510.8, 510.9), 1),
            ((3, 10, 410, 256), 0.5),
        ]:
            ref = self.gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = self.gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=3.0
            )

            with self.assertRaises(AssertionError):
                self.assert_image_equal(ref, im)

            self.assert_image_similar(ref, im, epsilon)

    def test_reducing_gap_8(self):
        for box in [None, (1.1, 2.2, 510.8, 510.9), (3, 10, 410, 256)]:
            ref = self.gradients_image.resize((52, 34), Image.BICUBIC, box=box)
            im = self.gradients_image.resize(
                (52, 34), Image.BICUBIC, box=box, reducing_gap=8.0
            )

            self.assert_image_equal(ref, im)

    def test_box_filter(self):
        for box, epsilon in [
            ((0, 0, 512, 512), 5.5),
            ((0.9, 1.7, 128, 128), 9.5),
        ]:
            ref = self.gradients_image.resize((52, 34), Image.BOX, box=box)
            im = self.gradients_image.resize(
                (52, 34), Image.BOX, box=box, reducing_gap=1.0
            )

            self.assert_image_similar(ref, im, epsilon)


class TestImageResize(PillowTestCase):
    def test_resize(self):
        def resize(mode, size):
            out = hopper(mode).resize(size)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, size)

        for mode in "1", "P", "L", "RGB", "I", "F":
            resize(mode, (112, 103))
            resize(mode, (188, 214))

        # Test unknown resampling filter
        with hopper() as im:
            self.assertRaises(ValueError, im.resize, (10, 10), "unknown")

    def test_default_filter(self):
        for mode in "L", "RGB", "I", "F":
            im = hopper(mode)
            self.assertEqual(im.resize((20, 20), Image.BICUBIC), im.resize((20, 20)))

        for mode in "1", "P":
            im = hopper(mode)
            self.assertEqual(im.resize((20, 20), Image.NEAREST), im.resize((20, 20)))
