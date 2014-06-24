from helper import unittest, PillowTestCase, tearDownModule, lena


class TestImageGetPalette(PillowTestCase):

    def test_palette(self):
        def palette(mode):
            p = lena(mode).getpalette()
            if p:
                return p[:10]
            return None
        self.assertEqual(palette("1"), None)
        self.assertEqual(palette("L"), None)
        self.assertEqual(palette("I"), None)
        self.assertEqual(palette("F"), None)
        self.assertEqual(palette("P"), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(palette("RGB"), None)
        self.assertEqual(palette("RGBA"), None)
        self.assertEqual(palette("CMYK"), None)
        self.assertEqual(palette("YCbCr"), None)


if __name__ == '__main__':
    unittest.main()

# End of file
