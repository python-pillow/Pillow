from helper import unittest, PillowTestCase

from PIL import Image


class TestFileSun(PillowTestCase):

    def test_sanity(self):
        # Arrange
        # Created with ImageMagick: convert hopper.jpg hopper.ras
        test_file = "Tests/images/hopper.ras"

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (128, 128))


if __name__ == '__main__':
    unittest.main()

# End of file
