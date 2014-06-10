from helper import unittest, PillowTestCase, tearDownModule, lena


class TestImageGetColors(PillowTestCase):

    def test_getcolors(self):

        def getcolors(mode, limit=None):
            im = lena(mode)
            if limit:
                colors = im.getcolors(limit)
            else:
                colors = im.getcolors()
            if colors:
                return len(colors)
            return None

        self.assertEqual(getcolors("1"), 2)
        self.assertEqual(getcolors("L"), 193)
        self.assertEqual(getcolors("I"), 193)
        self.assertEqual(getcolors("F"), 193)
        self.assertEqual(getcolors("P"), 54)  # fixed palette
        self.assertEqual(getcolors("RGB"), None)
        self.assertEqual(getcolors("RGBA"), None)
        self.assertEqual(getcolors("CMYK"), None)
        self.assertEqual(getcolors("YCbCr"), None)

        self.assertEqual(getcolors("L", 128), None)
        self.assertEqual(getcolors("L", 1024), 193)

        self.assertEqual(getcolors("RGB", 8192), None)
        self.assertEqual(getcolors("RGB", 16384), 14836)
        self.assertEqual(getcolors("RGB", 100000), 14836)

        self.assertEqual(getcolors("RGBA", 16384), 14836)
        self.assertEqual(getcolors("CMYK", 16384), 14836)
        self.assertEqual(getcolors("YCbCr", 16384), 11995)

    # --------------------------------------------------------------------

    def test_pack(self):
        # Pack problems for small tables (@PIL209)

        im = lena().quantize(3).convert("RGB")

        expected = [
            (3236, (227, 183, 147)),
            (6297, (143, 84, 81)),
            (6851, (208, 143, 112))]

        A = im.getcolors(maxcolors=2)
        self.assertEqual(A, None)

        A = im.getcolors(maxcolors=3)
        A.sort()
        self.assertEqual(A, expected)

        A = im.getcolors(maxcolors=4)
        A.sort()
        self.assertEqual(A, expected)

        A = im.getcolors(maxcolors=8)
        A.sort()
        self.assertEqual(A, expected)

        A = im.getcolors(maxcolors=16)
        A.sort()
        self.assertEqual(A, expected)


if __name__ == '__main__':
    unittest.main()

# End of file
