from helper import unittest, PillowTestCase, hopper


class TestImageGetExtrema(PillowTestCase):

    def test_extrema(self):

        def extrema(mode):
            return hopper(mode).getextrema()

        self.assertEqual(extrema("1"), (0, 255))
        self.assertEqual(extrema("L"), (0, 255))
        self.assertEqual(extrema("I"), (0, 255))
        self.assertEqual(extrema("F"), (0, 255))
        self.assertEqual(extrema("P"), (0, 225))  # fixed palette
        self.assertEqual(
            extrema("RGB"), ((0, 255), (0, 255), (0, 255)))
        self.assertEqual(
            extrema("RGBA"), ((0, 255), (0, 255), (0, 255), (255, 255)))
        self.assertEqual(
            extrema("CMYK"), (((0, 255), (0, 255), (0, 255), (0, 0))))


if __name__ == '__main__':
    unittest.main()
