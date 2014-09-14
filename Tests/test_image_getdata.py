from helper import unittest, PillowTestCase, hopper


class TestImageGetData(PillowTestCase):

    def test_sanity(self):

        data = hopper().getdata()

        len(data)
        list(data)

        self.assertEqual(data[0], (20, 20, 70))

    def test_roundtrip(self):

        def getdata(mode):
            im = hopper(mode).resize((32, 30))
            data = im.getdata()
            return data[0], len(data), len(list(data))

        self.assertEqual(getdata("1"), (0, 960, 960))
        self.assertEqual(getdata("L"), (25, 960, 960))
        self.assertEqual(getdata("I"), (25, 960, 960))
        self.assertEqual(getdata("F"), (25.0, 960, 960))
        self.assertEqual(getdata("RGB"), (((20, 20, 70), 960, 960)))
        self.assertEqual(getdata("RGBA"), ((20, 20, 70, 255), 960, 960))
        self.assertEqual(getdata("CMYK"), ((235, 235, 185, 0), 960, 960))
        self.assertEqual(getdata("YCbCr"), ((25, 153, 123), 960, 960))


if __name__ == '__main__':
    unittest.main()

# End of file
