from helper import unittest, PillowTestCase, tearDownModule, lena


class TestImageGetExtrema(PillowTestCase):

    def test_extrema(self):

        def extrema(mode):
            return lena(mode).getextrema()

        self.assertEqual(extrema("1"), (0, 255))
        self.assertEqual(extrema("L"), (40, 235))
        self.assertEqual(extrema("I"), (40, 235))
        self.assertEqual(extrema("F"), (40.0, 235.0))
        self.assertEqual(extrema("P"), (11, 218))  # fixed palette
        self.assertEqual(
            extrema("RGB"), ((61, 255), (26, 234), (44, 223)))
        self.assertEqual(
            extrema("RGBA"), ((61, 255), (26, 234), (44, 223), (255, 255)))
        self.assertEqual(
            extrema("CMYK"), ((0, 194), (21, 229), (32, 211), (0, 0)))


if __name__ == '__main__':
    unittest.main()

# End of file
