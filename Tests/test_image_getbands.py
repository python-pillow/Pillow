from helper import unittest, PillowTestCase

from PIL import Image


class TestImageGetBands(PillowTestCase):

    def test_getbands(self):
        self.assertEqual(Image.new("1", (1, 1)).getbands(), ("1",))
        self.assertEqual(Image.new("L", (1, 1)).getbands(), ("L",))
        self.assertEqual(Image.new("I", (1, 1)).getbands(), ("I",))
        self.assertEqual(Image.new("F", (1, 1)).getbands(), ("F",))
        self.assertEqual(Image.new("P", (1, 1)).getbands(), ("P",))
        self.assertEqual(Image.new("RGB", (1, 1)).getbands(), ("R", "G", "B"))
        self.assertEqual(
            Image.new("RGBA", (1, 1)).getbands(), ("R", "G", "B", "A"))
        self.assertEqual(
            Image.new("CMYK", (1, 1)).getbands(), ("C", "M", "Y", "K"))
        self.assertEqual(
            Image.new("YCbCr", (1, 1)).getbands(), ("Y", "Cb", "Cr"))


if __name__ == '__main__':
    unittest.main()
