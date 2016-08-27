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
        self.assertEqual(getdata("L"), (16, 960, 960))
        self.assertEqual(getdata("I"), (16, 960, 960))
        self.assertEqual(getdata("F"), (16.0, 960, 960))
        self.assertEqual(getdata("RGB"), (((11, 13, 52), 960, 960)))
        self.assertEqual(getdata("RGBA"), ((11, 13, 52, 255), 960, 960))
        self.assertEqual(getdata("CMYK"), ((244, 242, 203, 0), 960, 960))
        self.assertEqual(getdata("YCbCr"), ((16, 147, 123), 960, 960))


if __name__ == '__main__':
    unittest.main()
