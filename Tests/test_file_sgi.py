from helper import unittest, PillowTestCase

from PIL import Image, SgiImagePlugin


class TestFileSgi(PillowTestCase):

    def test_rgb(self):
        # Arrange
        # Created with ImageMagick then renamed:
        # convert hopper.ppm hopper.sgi
        test_file = "Tests/images/hopper.rgb"

        # Act / Assert
        self.assertRaises(ValueError, lambda: Image.open(test_file))

    def test_l(self):
        # Arrange
        # Created with ImageMagick then renamed:
        # convert hopper.ppm -monochrome hopper.sgi
        test_file = "Tests/images/hopper.bw"

        # Act / Assert
        self.assertRaises(ValueError, lambda: Image.open(test_file))

    def test_rgba(self):
        # Arrange
        # Created with ImageMagick:
        # convert transparent.png transparent.sgi
        test_file = "Tests/images/transparent.sgi"

        # Act / Assert
        self.assertRaises(ValueError, lambda: Image.open(test_file))

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(ValueError,
                          lambda:
                          SgiImagePlugin.SgiImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()

# End of file
