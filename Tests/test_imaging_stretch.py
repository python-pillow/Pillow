"""
Tests for ImagingCore.stretch functionality.
"""
from itertools import permutations

from helper import unittest, PillowTestCase

from PIL import Image


im = Image.open("Tests/images/hopper.ppm").copy()


class TestImagingStretch(PillowTestCase):

    def stretch(self, im, size, f):
        return im._new(im.im.stretch(size, f))

    def test_modes(self):
        self.assertRaises(ValueError, im.convert("1").im.stretch,
                          (15, 12), Image.ANTIALIAS)
        self.assertRaises(ValueError, im.convert("P").im.stretch,
                          (15, 12), Image.ANTIALIAS)
        for mode in ["L", "I", "F", "RGB", "RGBA", "CMYK", "YCbCr"]:
            s = im.convert(mode).im
            r = s.stretch((15, 12), Image.ANTIALIAS)
            self.assertEqual(r.mode, mode)
            self.assertEqual(r.size, (15, 12))
            self.assertEqual(r.bands, s.bands)

    def test_reduce_filters(self):
        # There is no Image.NEAREST because im.stretch implementation
        # is not NEAREST for reduction. It should be removed
        # or renamed to supersampling.
        for f in [Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS]:
            r = im.im.stretch((15, 12), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (15, 12))

    def test_enlarge_filters(self):
        for f in [Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS]:
            r = im.im.stretch((764, 414), f)
            self.assertEqual(r.mode, "RGB")
            self.assertEqual(r.size, (764, 414))

    def test_endianness(self):
        # Make an image with one colored pixel, in one channel.
        # When stretched, that channel should be the same as a GS image.
        # Other channels should be unaffected.
        # The R and A channels should not swap, which is indicitive of
        # an endianness issues.

        samples = {
            'blank': Image.new('L', (2, 2), 0),
            'filled': Image.new('L', (2, 2), 255),
            'dirty': Image.new('L', (2, 2), 0),
        }
        samples['dirty'].putpixel((1, 1), 128)

        for f in [Image.BILINEAR, Image.BICUBIC, Image.ANTIALIAS]:
            # samples resized with current filter
            resized = dict(
                (name, self.stretch(ch, (4, 4), f))
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
                    stretched = self.stretch(im, (4, 4), f)

                    for i, ch in enumerate(stretched.split()):
                        # check what resized channel in image is the same
                        # as separately resized channel
                        self.assert_image_equal(ch, resized[channels[i]])


if __name__ == '__main__':
    unittest.main()

# End of file
