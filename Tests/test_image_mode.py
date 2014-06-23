from helper import unittest, PillowTestCase, tearDownModule, lena

from PIL import Image


class TestImageMode(PillowTestCase):

    def test_sanity(self):

        im = lena()
        im.mode

    def test_properties(self):
        def check(mode, *result):
            signature = (
                Image.getmodebase(mode), Image.getmodetype(mode),
                Image.getmodebands(mode), Image.getmodebandnames(mode),
                )
            self.assertEqual(signature, result)
        check("1", "L", "L", 1, ("1",))
        check("L", "L", "L", 1, ("L",))
        check("P", "RGB", "L", 1, ("P",))
        check("I", "L", "I", 1, ("I",))
        check("F", "L", "F", 1, ("F",))
        check("RGB", "RGB", "L", 3, ("R", "G", "B"))
        check("RGBA", "RGB", "L", 4, ("R", "G", "B", "A"))
        check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
        check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
        check("CMYK", "RGB", "L", 4, ("C", "M", "Y", "K"))
        check("YCbCr", "RGB", "L", 3, ("Y", "Cb", "Cr"))


if __name__ == '__main__':
    unittest.main()

# End of file
