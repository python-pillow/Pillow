from helper import unittest, PillowTestCase

from PIL import Image


class TestFileSgi(PillowTestCase):

    def test_rgb(self):
        # Arrange
        # Created with ImageMagick then renamed:
        # convert lena.ppm lena.sgi
        test_file = "Tests/images/lena.rgb"

        # Act / Assert
        self.assertRaises(ValueError, lambda: Image.open(test_file))

    def test_l(self):
        # Arrange
        # Created with ImageMagick then renamed:
        # convert lena.ppm -monochrome lena.sgi
        test_file = "Tests/images/lena.bw"

        # Act / Assert
        self.assertRaises(ValueError, lambda: Image.open(test_file))

    def test_rgba(self):
        # Arrange
        # Created with ImageMagick:
        # convert transparent.png transparent.sgi
        test_file = "Tests/images/transparent.sgi"

        # Act / Assert
        self.assertRaises(ValueError, lambda: Image.open(test_file))


if __name__ == '__main__':
    unittest.main()

# End of file
