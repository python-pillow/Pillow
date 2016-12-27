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

    def test_crop_float(self):
        # Check cropping floats are rounded to nearest integer
        # https://github.com/python-pillow/Pillow/issues/1744

        # Arrange
        im = Image.new("RGB", (10, 10))
        self.assertEqual(im.size, (10, 10))

        # Act
        cropped = im.crop((0.9, 1.1, 4.2, 5.8))

        # Assert
        self.assertEqual(cropped.size, (3, 5))

    def test_crop_crash(self):
        #Image.crop crashes prepatch with an access violation
        #apparently a use after free on windows, see
        #https://github.com/python-pillow/Pillow/issues/1077
        
        test_img = 'Tests/images/bmp/g/pal8-0.bmp'
        extents = (1,1,10,10)
        #works prepatch
        img = Image.open(test_img)
        img2 = img.crop(extents)
        img2.load()
        
        # fail prepatch
        img = Image.open(test_img)
        img = img.crop(extents)
        img.load()

    def test_crop_zero(self):
        
        im = Image.new('RGB', (0, 0), 'white')
        
        cropped = im.crop((0, 0, 0, 0))
        self.assertEqual(cropped.size, (0, 0))

        cropped = im.crop((10, 10, 20, 20))
        self.assertEqual(cropped.size, (10, 10))
        self.assertEqual(cropped.getdata()[0], (0, 0, 0))

        im = Image.new('RGB', (0, 0))
        
        cropped = im.crop((10, 10, 20, 20))
        self.assertEqual(cropped.size, (10, 10))
        self.assertEqual(cropped.getdata()[2], (0, 0, 0))



if __name__ == '__main__':
    unittest.main()
