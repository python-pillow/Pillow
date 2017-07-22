from helper import unittest, PillowTestCase, hopper


class TestImageGetPalette(PillowTestCase):

    def test_palette(self):
        def palette(mode):
            p = hopper(mode).getpalette()
            if p:
                return p[:10]
            return None
        self.assertIsNone(palette("1"))
        self.assertIsNone(palette("L"))
        self.assertIsNone(palette("I"))
        self.assertIsNone(palette("F"))
        self.assertEqual(palette("P"), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertIsNone(palette("RGB"))
        self.assertIsNone(palette("RGBA"))
        self.assertIsNone(palette("CMYK"))
        self.assertIsNone(palette("YCbCr"))


if __name__ == '__main__':
    unittest.main()
