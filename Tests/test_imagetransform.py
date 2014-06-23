from helper import unittest, PillowTestCase, tearDownModule

from PIL import Image
from PIL import ImageTransform


class TestImageTransform(PillowTestCase):

    def test_sanity(self):
        im = Image.new("L", (100, 100))

        seq = tuple(range(10))

        transform = ImageTransform.AffineTransform(seq[:6])
        im.transform((100, 100), transform)
        transform = ImageTransform.ExtentTransform(seq[:4])
        im.transform((100, 100), transform)
        transform = ImageTransform.QuadTransform(seq[:8])
        im.transform((100, 100), transform)
        transform = ImageTransform.MeshTransform([(seq[:4], seq[:8])])
        im.transform((100, 100), transform)


if __name__ == '__main__':
    unittest.main()

# End of file
