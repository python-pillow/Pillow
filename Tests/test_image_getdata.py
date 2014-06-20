from helper import unittest, PillowTestCase, tearDownModule, lena


class TestImageGetData(PillowTestCase):

    def test_sanity(self):

        data = lena().getdata()

        len(data)
        list(data)

        self.assertEqual(data[0], (223, 162, 133))

    def test_roundtrip(self):

        def getdata(mode):
            im = lena(mode).resize((32, 30))
            data = im.getdata()
            return data[0], len(data), len(list(data))

        self.assertEqual(getdata("1"), (255, 960, 960))
        self.assertEqual(getdata("L"), (176, 960, 960))
        self.assertEqual(getdata("I"), (176, 960, 960))
        self.assertEqual(getdata("F"), (176.0, 960, 960))
        self.assertEqual(getdata("RGB"), ((223, 162, 133), 960, 960))
        self.assertEqual(getdata("RGBA"), ((223, 162, 133, 255), 960, 960))
        self.assertEqual(getdata("CMYK"), ((32, 93, 122, 0), 960, 960))
        self.assertEqual(getdata("YCbCr"), ((176, 103, 160), 960, 960))


if __name__ == '__main__':
    unittest.main()

# End of file
