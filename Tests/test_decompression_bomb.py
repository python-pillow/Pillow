from helper import unittest, PillowTestCase, hopper

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
        self.assertIsNone(Image.MAX_IMAGE_PIXELS)

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
        self.assert_warning(Image.DecompressionBombWarning,
                            Image.open, TEST_FILE)

class TestDecompressionCrop(PillowTestCase):

    def setUp(self):
        self.src = hopper()
        Image.MAX_IMAGE_PIXELS = self.src.height * self.src.width

    def tearDown(self):
        Image.MAX_IMAGE_PIXELS = ORIGINAL_LIMIT

    def testEnlargeCrop(self):
        # Crops can extend the extents, therefore we should have the
        # same decompression bomb warnings on them.
        box = (0, 0, self.src.width * 2, self.src.height * 2)
        self.assert_warning(Image.DecompressionBombWarning,
                            self.src.crop, box)

if __name__ == '__main__':
    unittest.main()
