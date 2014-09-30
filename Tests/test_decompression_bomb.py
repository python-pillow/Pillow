from helper import unittest, PillowTestCase

from PIL import Image

TEST_FILE = "Tests/images/hopper.ppm"

ORIGINAL_LIMIT = Image.MAX_IMAGE_PIXELS


class TestDecompressionBomb(PillowTestCase):

    def tearDown(self):
        Image.MAX_IMAGE_PIXELS = ORIGINAL_LIMIT

    def test_no_warning_small_file(self):
        # Implicit assert: no warning.
        # A warning would cause a failure.
        Image.open(TEST_FILE)

    def test_no_warning_no_limit(self):
        # Arrange
        # Turn limit off
        Image.MAX_IMAGE_PIXELS = None
        self.assertEqual(Image.MAX_IMAGE_PIXELS, None)

        # Act / Assert
        # Implicit assert: no warning.
        # A warning would cause a failure.
        Image.open(TEST_FILE)

    def test_warning(self):
        # Arrange
        # Set limit to a low, easily testable value
        Image.MAX_IMAGE_PIXELS = 10
        self.assertEqual(Image.MAX_IMAGE_PIXELS, 10)

        # Act / Assert
        self.assert_warning(
            Image.DecompressionBombWarning,
            lambda: Image.open(TEST_FILE))

if __name__ == '__main__':
    unittest.main()

# End of file
