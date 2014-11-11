from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageMode(PillowTestCase):

    def test_sanity(self):

        im = hopper()
        im.mode

        from PIL import ImageMode

        ImageMode.getmode("1")
        ImageMode.getmode("L")
        ImageMode.getmode("P")
        ImageMode.getmode("RGB")
        ImageMode.getmode("I")
        ImageMode.getmode("F")

        m = ImageMode.getmode("1")
        self.assertEqual(m.mode, "1")
        self.assertEqual(m.bands, ("1",))
        self.assertEqual(m.basemode, "L")
        self.assertEqual(m.basetype, "L")

        m = ImageMode.getmode("RGB")
        self.assertEqual(m.mode, "RGB")
        self.assertEqual(m.bands, ("R", "G", "B"))
        self.assertEqual(m.basemode, "RGB")
        self.assertEqual(m.basetype, "L")

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
