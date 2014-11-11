from helper import unittest, PillowTestCase

from PIL import Image


class TestImagePutAlpha(PillowTestCase):

    def test_interface(self):

        im = Image.new("RGBA", (1, 1), (1, 2, 3, 0))
        self.assertEqual(im.getpixel((0, 0)), (1, 2, 3, 0))

        im = Image.new("RGBA", (1, 1), (1, 2, 3))
        self.assertEqual(im.getpixel((0, 0)), (1, 2, 3, 255))

        im.putalpha(Image.new("L", im.size, 4))
        self.assertEqual(im.getpixel((0, 0)), (1, 2, 3, 4))

        im.putalpha(5)
        self.assertEqual(im.getpixel((0, 0)), (1, 2, 3, 5))

    def test_promote(self):

        im = Image.new("L", (1, 1), 1)
        self.assertEqual(im.getpixel((0, 0)), 1)

        im.putalpha(2)
        self.assertEqual(im.mode, 'LA')
        self.assertEqual(im.getpixel((0, 0)), (1, 2))

        im = Image.new("RGB", (1, 1), (1, 2, 3))
        self.assertEqual(im.getpixel((0, 0)), (1, 2, 3))

        im.putalpha(4)
        self.assertEqual(im.mode, 'RGBA')
        self.assertEqual(im.getpixel((0, 0)), (1, 2, 3, 4))

    def test_readonly(self):

        im = Image.new("RGB", (1, 1), (1, 2, 3))
        im.readonly = 1

        im.putalpha(4)
        self.assertFalse(im.readonly)
        self.assertEqual(im.mode, 'RGBA')
        self.assertEqual(im.getpixel((0, 0)), (1, 2, 3, 4))


if __name__ == '__main__':
    unittest.main()

# End of file
