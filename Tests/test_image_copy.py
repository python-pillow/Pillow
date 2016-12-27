from helper import unittest, PillowTestCase, hopper

from PIL import Image

import copy


class TestImageCopy(PillowTestCase):

    def test_copy(self):
        croppedCoordinates = (10, 10, 20, 20)
        croppedSize = (10, 10)
        for mode in "1", "P", "L", "RGB", "I", "F":
            # Internal copy method
            im = hopper(mode)
            out = im.copy()
            self.assertEqual(out.mode, im.mode)
            self.assertEqual(out.size, im.size)

            # Python's copy method
            im = hopper(mode)
            out = copy.copy(im)
            self.assertEqual(out.mode, im.mode)
            self.assertEqual(out.size, im.size)

            # Internal copy method on a cropped image
            im = hopper(mode)
            out = im.crop(croppedCoordinates).copy()
            self.assertEqual(out.mode, im.mode)
            self.assertEqual(out.size, croppedSize)

            # Python's copy method on a cropped image
            im = hopper(mode)
            out = copy.copy(im.crop(croppedCoordinates))
            self.assertEqual(out.mode, im.mode)
            self.assertEqual(out.size, croppedSize)

    def test_copy_zero(self):
        im = Image.new('RGB', (0,0))
        out = im.copy()
        self.assertEqual(out.mode, im.mode)
        self.assertEqual(out.size, im.size)


if __name__ == '__main__':
    unittest.main()
