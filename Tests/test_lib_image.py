from helper import unittest, PillowTestCase

from PIL import Image


class TestLibImage(PillowTestCase):

    def test_setmode(self):

        im = Image.new("L", (1, 1), 255)
        im.im.setmode("1")
        self.assertEqual(im.im.getpixel((0, 0)), 255)
        im.im.setmode("L")
        self.assertEqual(im.im.getpixel((0, 0)), 255)

        im = Image.new("1", (1, 1), 1)
        im.im.setmode("L")
        self.assertEqual(im.im.getpixel((0, 0)), 255)
        im.im.setmode("1")
        self.assertEqual(im.im.getpixel((0, 0)), 255)

        im = Image.new("RGB", (1, 1), (1, 2, 3))
        im.im.setmode("RGB")
        self.assertEqual(im.im.getpixel((0, 0)), (1, 2, 3))
        im.im.setmode("RGBA")
        self.assertEqual(im.im.getpixel((0, 0)), (1, 2, 3, 255))
        im.im.setmode("RGBX")
        self.assertEqual(im.im.getpixel((0, 0)), (1, 2, 3, 255))
        im.im.setmode("RGB")
        self.assertEqual(im.im.getpixel((0, 0)), (1, 2, 3))

        self.assertRaises(ValueError, lambda: im.im.setmode("L"))
        self.assertRaises(ValueError, lambda: im.im.setmode("RGBABCDE"))


if __name__ == '__main__':
    unittest.main()
