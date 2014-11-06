"""
Tests for ImagingCore.stretch functionality.
"""

from helper import unittest, PillowTestCase

from PIL import Image


im = Image.open("Tests/images/hopper.ppm").copy()


class TestImagingStretch(PillowTestCase):

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


if __name__ == '__main__':
    unittest.main()

# End of file
