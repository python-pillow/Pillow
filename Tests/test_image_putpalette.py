from helper import unittest, PillowTestCase, hopper

from PIL import ImagePalette


class TestImagePutPalette(PillowTestCase):

    def test_putpalette(self):
        def palette(mode):
            im = hopper(mode).copy()
            im.putpalette(list(range(256))*3)
            p = im.getpalette()
            if p:
                return im.mode, p[:10]
            return im.mode
        self.assertRaises(ValueError, lambda: palette("1"))
        self.assertEqual(palette("L"), ("P", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
        self.assertEqual(palette("P"), ("P", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
        self.assertRaises(ValueError, lambda: palette("I"))
        self.assertRaises(ValueError, lambda: palette("F"))
        self.assertRaises(ValueError, lambda: palette("RGB"))
        self.assertRaises(ValueError, lambda: palette("RGBA"))
        self.assertRaises(ValueError, lambda: palette("YCbCr"))

    def test_imagepalette(self):
        im = hopper("P")
        im.putpalette(ImagePalette.negative())
        im.putpalette(ImagePalette.random())
        im.putpalette(ImagePalette.sepia())
        im.putpalette(ImagePalette.wedge())


if __name__ == '__main__':
    unittest.main()
