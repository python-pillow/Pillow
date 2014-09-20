from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageCrop(PillowTestCase):

    def test_crop(self):
        def crop(mode):
            out = hopper(mode).crop((50, 50, 100, 100))
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, (50, 50))
        for mode in "1", "P", "L", "RGB", "I", "F":
            crop(mode)

    def test_wide_crop(self):

        def crop(*bbox):
            i = im.crop(bbox)
            h = i.histogram()
            while h and not h[-1]:
                del h[-1]
            return tuple(h)

        im = Image.new("L", (100, 100), 1)

        self.assertEqual(crop(0, 0, 100, 100), (0, 10000))
        self.assertEqual(crop(25, 25, 75, 75), (0, 2500))

        # sides
        self.assertEqual(crop(-25, 0, 25, 50), (1250, 1250))
        self.assertEqual(crop(0, -25, 50, 25), (1250, 1250))
        self.assertEqual(crop(75, 0, 125, 50), (1250, 1250))
        self.assertEqual(crop(0, 75, 50, 125), (1250, 1250))

        self.assertEqual(crop(-25, 25, 125, 75), (2500, 5000))
        self.assertEqual(crop(25, -25, 75, 125), (2500, 5000))

        # corners
        self.assertEqual(crop(-25, -25, 25, 25), (1875, 625))
        self.assertEqual(crop(75, -25, 125, 25), (1875, 625))
        self.assertEqual(crop(75, 75, 125, 125), (1875, 625))
        self.assertEqual(crop(-25, 75, 25, 125), (1875, 625))

    def test_negative_crop(self):
        # Check negative crop size (@PIL171)

        im = Image.new("L", (512, 512))
        im = im.crop((400, 400, 200, 200))

        self.assertEqual(im.size, (0, 0))
        self.assertEqual(len(im.getdata()), 0)
        self.assertRaises(IndexError, lambda: im.getdata()[0])


if __name__ == '__main__':
    unittest.main()

# End of file
