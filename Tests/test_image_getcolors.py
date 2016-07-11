from helper import unittest, PillowTestCase, hopper


class TestImageGetColors(PillowTestCase):

    def test_getcolors(self):

        def getcolors(mode, limit=None):
            im = hopper(mode)
            if limit:
                colors = im.getcolors(limit)
            else:
                colors = im.getcolors()
            if colors:
                return len(colors)
            return None

        self.assertEqual(getcolors("1"), 2)
        self.assertEqual(getcolors("L"), 255)
        self.assertEqual(getcolors("I"), 255)
        self.assertEqual(getcolors("F"), 255)
        self.assertEqual(getcolors("P"), 90)  # fixed palette
        self.assertEqual(getcolors("RGB"), None)
        self.assertEqual(getcolors("RGBA"), None)
        self.assertEqual(getcolors("CMYK"), None)
        self.assertEqual(getcolors("YCbCr"), None)

        self.assertEqual(getcolors("L", 128), None)
        self.assertEqual(getcolors("L", 1024), 255)

        self.assertEqual(getcolors("RGB", 8192), None)
        self.assertEqual(getcolors("RGB", 16384), 10100)
        self.assertEqual(getcolors("RGB", 100000), 10100)

        self.assertEqual(getcolors("RGBA", 16384), 10100)
        self.assertEqual(getcolors("CMYK", 16384), 10100)
        self.assertEqual(getcolors("YCbCr", 16384), 9329)

    # --------------------------------------------------------------------

    def test_pack(self):
        # Pack problems for small tables (@PIL209)

        im = hopper().quantize(3).convert("RGB")

        expected = [(4039, (172, 166, 181)),
                    (4385, (124, 113, 134)),
                    (7960, (31, 20, 33))]

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
