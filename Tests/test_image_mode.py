from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageMode(PillowTestCase):
    def test_sanity(self):

        with hopper() as im:
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
        self.assertEqual(str(m), "1")
        self.assertEqual(m.bands, ("1",))
        self.assertEqual(m.basemode, "L")
        self.assertEqual(m.basetype, "L")

        for mode in (
            "I;16",
            "I;16S",
            "I;16L",
            "I;16LS",
            "I;16B",
            "I;16BS",
            "I;16N",
            "I;16NS",
        ):
            m = ImageMode.getmode(mode)
            self.assertEqual(m.mode, mode)
            self.assertEqual(str(m), mode)
            self.assertEqual(m.bands, ("I",))
            self.assertEqual(m.basemode, "L")
            self.assertEqual(m.basetype, "L")

        m = ImageMode.getmode("RGB")
        self.assertEqual(m.mode, "RGB")
        self.assertEqual(str(m), "RGB")
        self.assertEqual(m.bands, ("R", "G", "B"))
        self.assertEqual(m.basemode, "RGB")
        self.assertEqual(m.basetype, "L")

    def test_properties(self):
        def check(mode, *result):
            signature = (
                Image.getmodebase(mode),
                Image.getmodetype(mode),
                Image.getmodebands(mode),
                Image.getmodebandnames(mode),
            )
            self.assertEqual(signature, result)

        check("1", "L", "L", 1, ("1",))
        check("L", "L", "L", 1, ("L",))
        check("P", "P", "L", 1, ("P",))
        check("I", "L", "I", 1, ("I",))
        check("F", "L", "F", 1, ("F",))
        check("RGB", "RGB", "L", 3, ("R", "G", "B"))
        check("RGBA", "RGB", "L", 4, ("R", "G", "B", "A"))
        check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
        check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
        check("CMYK", "RGB", "L", 4, ("C", "M", "Y", "K"))
        check("YCbCr", "RGB", "L", 3, ("Y", "Cb", "Cr"))
