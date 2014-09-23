from helper import unittest, PillowTestCase, hopper


class TestImageHistogram(PillowTestCase):

    def test_histogram(self):

        def histogram(mode):
            h = hopper(mode).histogram()
            return len(h), min(h), max(h)

        self.assertEqual(histogram("1"), (256, 0, 10994))
        self.assertEqual(histogram("L"), (256, 0, 638))
        self.assertEqual(histogram("I"), (256, 0, 638))
        self.assertEqual(histogram("F"), (256, 0, 638))
        self.assertEqual(histogram("P"), (256, 0, 1871))
        self.assertEqual(histogram("RGB"), (768, 4, 675))
        self.assertEqual(histogram("RGBA"), (1024, 0, 16384))
        self.assertEqual(histogram("CMYK"), (1024, 0, 16384))
        self.assertEqual(histogram("YCbCr"), (768, 0, 1908))


if __name__ == '__main__':
    unittest.main()

# End of file
