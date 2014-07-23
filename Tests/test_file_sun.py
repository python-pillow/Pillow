from helper import unittest, PillowTestCase

from PIL import Image


class TestFileSun(PillowTestCase):

    def test_sanity(self):
        # Arrange
        # Created with ImageMagick: convert lena.ppm lena.ras
        test_file = "Tests/images/lena.ras"

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (128, 128))


if __name__ == '__main__':
    unittest.main()

# End of file
