"""
Tests for resize functionality.
"""
from itertools import permutations

from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImagingCoreResize(PillowTestCase):

    def resize(self, im, size, f):
        # Image class independent version of resize.
        im.load()
        return im._new(im.im.resize(size, f))

    def test_nearest_mode(self):
        for mode in ["1", "P", "L", "I", "F", "RGB", "RGBA", "CMYK", "YCbCr",
                     "I;16"]:  # exotic mode
            im = hopper(mode)
            r = self.resize(im, (15, 12), Image.NEAREST)
            self.assertEqual(r.mode, mode)
            self.assertEqual(r.size, (15, 12))
            self.assertEqual(r.im.bands, im.im.bands)

    def test_convolution_modes(self):
        self.assertRaises(ValueError, self.resize, hopper("1"),
                          (15, 12), Image.BILINEAR)
        self.assertRaises(ValueError, self.resize, hopper("P"),
                          (15, 12), Image.BILINEAR)
        self.assertRaises(ValueError, self.resize, hopper("I;16"),
                          (15, 12), Image.BILINEAR)
        for mode in ["L", "I", "F", "RGB", "RGBA", "CMYK", "YCbCr"]:
            im = hopper(mode)
            r = self.resize(im, (15, 12), Image.BILINEAR)
            self.assertEqual(r.mode, mode)
            self.assertEqual(r.size, (15, 12))
            self.assertEqual(r.im.bands, im.im.bands)

    def test_reduce_filters(self):
        for f in [Image.LINEAR, Image.BILINEAR, Image.BICUBIC, Image.LANCZOS]:
            r = self.resize(hopper("RGB"), (15, 12), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (15, 12))

    def test_enlarge_filters(self):
        for f in [Image.LINEAR, Image.BILINEAR, Image.BICUBIC, Image.LANCZOS]:
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
            'blank': Image.new('L', (2, 2), 0),
            'filled': Image.new('L', (2, 2), 255),
            'dirty': Image.new('L', (2, 2), 0),
        }
        samples['dirty'].putpixel((1, 1), 128)

        for f in [Image.LINEAR, Image.BILINEAR, Image.BICUBIC, Image.LANCZOS]:
            # samples resized with current filter
            references = dict(
                (name, self.resize(ch, (4, 4), f))
                for name, ch in samples.items()
            )

            for mode, channels_set in [
                ('RGB', ('blank', 'filled', 'dirty')),
                ('RGBA', ('blank', 'blank', 'filled', 'dirty')),
                ('LA', ('filled', 'dirty')),
            ]:
                for channels in set(permutations(channels_set)):
                    # compile image from different channels permutations
                    im = Image.merge(mode, [samples[ch] for ch in channels])
                    resized = self.resize(im, (4, 4), f)

                    for i, ch in enumerate(resized.split()):
                        # check what resized channel in image is the same
                        # as separately resized channel
                        self.assert_image_equal(ch, references[channels[i]])


class TestImageResize(PillowTestCase):

    def test_resize(self):
        def resize(mode, size):
            out = hopper(mode).resize(size)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, size)
        for mode in "1", "P", "L", "RGB", "I", "F":
            resize(mode, (112, 103))
            resize(mode, (188, 214))


if __name__ == '__main__':
    unittest.main()

# End of file
