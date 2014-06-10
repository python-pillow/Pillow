from helper import unittest, PillowTestCase, tearDownModule

from PIL import ImageMode


class TestImageMode(PillowTestCase):

    def test_sanity(self):
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


if __name__ == '__main__':
    unittest.main()

# End of file
