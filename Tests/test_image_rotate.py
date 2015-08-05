from helper import unittest, PillowTestCase, hopper
from PIL import Image


class TestImageRotate(PillowTestCase):

    def test_rotate(self):
        def rotate(im, mode, angle):
            out = im.rotate(angle)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)  # default rotate clips output
            out = im.rotate(angle, expand=1)
            self.assertEqual(out.mode, mode)
            self.assertNotEqual(out.size, im.size)
        for mode in "1", "P", "L", "RGB", "I", "F":
            im = hopper(mode)
            rotate(im, mode, 45)
        for angle in 90, 270:
            im = Image.open('Tests/images/test-card.png')
            rotate(im, im.mode, angle)


if __name__ == '__main__':
    unittest.main()

# End of file
