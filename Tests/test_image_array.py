from helper import unittest, PillowTestCase, hopper

from PIL import Image

im = hopper().resize((128, 100))


class TestImageArray(PillowTestCase):

    def test_toarray(self):
        def test(mode):
            ai = im.convert(mode).__array_interface__
            return ai["shape"], ai["typestr"], len(ai["data"])
        # self.assertEqual(test("1"), ((100, 128), '|b1', 1600))
        self.assertEqual(test("L"), ((100, 128), '|u1', 12800))

        # FIXME: wrong?
        self.assertEqual(test("I"), ((100, 128), Image._ENDIAN + 'i4', 51200))
        # FIXME: wrong?
        self.assertEqual(test("F"), ((100, 128), Image._ENDIAN + 'f4', 51200))

        self.assertEqual(test("RGB"), ((100, 128, 3), '|u1', 38400))
        self.assertEqual(test("RGBA"), ((100, 128, 4), '|u1', 51200))
        self.assertEqual(test("RGBX"), ((100, 128, 4), '|u1', 51200))

    def test_fromarray(self):
        def test(mode):
            i = im.convert(mode)
            a = i.__array_interface__
            a["strides"] = 1  # pretend it's non-contigous
            i.__array_interface__ = a  # patch in new version of attribute
            out = Image.fromarray(i)
            return out.mode, out.size, list(i.getdata()) == list(out.getdata())
        # self.assertEqual(test("1"), ("1", (128, 100), True))
        self.assertEqual(test("L"), ("L", (128, 100), True))
        self.assertEqual(test("I"), ("I", (128, 100), True))
        self.assertEqual(test("F"), ("F", (128, 100), True))
        self.assertEqual(test("RGB"), ("RGB", (128, 100), True))
        self.assertEqual(test("RGBA"), ("RGBA", (128, 100), True))
        self.assertEqual(test("RGBX"), ("RGBA", (128, 100), True))


if __name__ == '__main__':
    unittest.main()

# End of file
