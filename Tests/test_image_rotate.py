from helper import unittest, PillowTestCase, hopper
from PIL import Image


class TestImageRotate(PillowTestCase):

    def rotate(self, im, mode, angle, center=None, translate=None):
        out = im.rotate(angle, center=center, translate=translate)
        self.assertEqual(out.mode, mode)
        self.assertEqual(out.size, im.size)  # default rotate clips output
        out = im.rotate(angle, center=center, translate=translate, expand=1)
        self.assertEqual(out.mode, mode)
        if angle % 180 == 0:
            self.assertEqual(out.size, im.size)
        elif im.size == (0, 0):
            self.assertEqual(out.size, im.size)
        else:
            self.assertNotEqual(out.size, im.size)

    def test_mode(self):                
        for mode in ("1", "P", "L", "RGB", "I", "F"):
            im = hopper(mode)
            self.rotate(im, mode, 45)

    def test_angle(self):
        for angle in (0, 90, 180, 270):
            im = Image.open('Tests/images/test-card.png')
            self.rotate(im, im.mode, angle)

    def test_zero(self):
        for angle in (0, 45, 90, 180, 270):
            im = Image.new('RGB',(0,0))
            self.rotate(im, im.mode, angle)

    def test_center(self):
        im = hopper()
        self.rotate(im, im.mode, 45, center=(0, 0))
        self.rotate(im, im.mode, 45, translate=(im.size[0]/2, 0))
        self.rotate(im, im.mode, 45, center=(0, 0), translate=(im.size[0]/2, 0))

    


if __name__ == '__main__':
    unittest.main()
