from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageGetProjection(PillowTestCase):

    def test_sanity(self):

        im = hopper()

        projection = im.getprojection()

        self.assertEqual(len(projection), 2)
        self.assertEqual(len(projection[0]), im.size[0])
        self.assertEqual(len(projection[1]), im.size[1])

        # 8-bit image
        im = Image.new("L", (10, 10))
        self.assertEqual(im.getprojection()[0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(im.getprojection()[1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        im.paste(255, (2, 4, 8, 6))
        self.assertEqual(im.getprojection()[0], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0])
        self.assertEqual(im.getprojection()[1], [0, 0, 0, 0, 1, 1, 0, 0, 0, 0])

        # 32-bit image
        im = Image.new("RGB", (10, 10))
        self.assertEqual(im.getprojection()[0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(im.getprojection()[1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        im.paste(255, (2, 4, 8, 6))
        self.assertEqual(im.getprojection()[0], [0, 0, 1, 1, 1, 1, 1, 1, 0, 0])
        self.assertEqual(im.getprojection()[1], [0, 0, 0, 0, 1, 1, 0, 0, 0, 0])


if __name__ == '__main__':
    unittest.main()

# End of file
