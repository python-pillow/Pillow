from helper import unittest, PillowTestCase

from PIL import Image


class TestFileSgi(PillowTestCase):

    def sanity(self, filename, expected_mode, expected_size=(128, 128)):
        # Act
        im = Image.open(filename)

        # Assert
        self.assertEqual(im.mode, expected_mode)
        self.assertEqual(im.size, expected_size)

    def test_rgb(self):
        # Arrange
        # Created with ImageMagick then renamed:
        # convert lena.ppm lena.sgi
        test_file = "Tests/images/lena.rgb"
        expected_mode = "RGB"

        # Act / Assert
        self.sanity(test_file, expected_mode)

    def test_l(self):
        # Arrange
        # Created with ImageMagick then renamed:
        # convert lena.ppm -monochrome lena.sgi
        test_file = "Tests/images/lena.bw"
        expected_mode = "L"

        # Act / Assert
        self.sanity(test_file, expected_mode)

    def test_rgba(self):
        # Arrange
        # Created with ImageMagick:
        # convert transparent.png transparent.sgi
        test_file = "Tests/images/transparent.sgi"
        expected_mode = "RGBA"
        expected_size = (200, 150)

        # Act / Assert
        self.sanity(test_file, expected_mode, expected_size)


if __name__ == '__main__':
    unittest.main()

# End of file
