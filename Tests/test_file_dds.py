from helper import unittest, PillowTestCase

from PIL import Image, DdsImagePlugin

TEST_FILE_DXT1 = "Tests/images/dxt1-rgb-4bbp-noalpha_MipMaps-1.dds"
TEST_FILE_DXT5 = "Tests/images/dxt5-argb-8bbp-interpolatedalpha_MipMaps-1.dds"


class TestFileCur(PillowTestCase):

    def test_sanity_dxt1(self):
        im = Image.open(TEST_FILE_DXT1)

        self.assertEqual(im.size, (256, 256))
        self.assertIsInstance(im, DdsImagePlugin.DdsImageFile)
        # Check some pixel colors to ensure image is loaded properly
        self.assertEqual(im.getpixel((10, 1)), (49, 50, 53, 44))
        self.assertEqual(im.getpixel((11, 1)), (32, 50, 53, 53))
        self.assertEqual(im.getpixel((16, 16)), (91, 48, 44, 32))

    def test_sanity_dxt5(self):
        im = Image.open(TEST_FILE_DXT5)

        self.assertEqual(im.size, (256, 256))
        self.assertIsInstance(im, DdsImagePlugin.DdsImageFile)
        # Check some pixel colors to ensure image is loaded properly
        self.assertEqual(im.getpixel((10, 1)), (49, 50, 53, 44))
        self.assertEqual(im.getpixel((11, 1)), (32, 49, 50, 56))
        self.assertEqual(im.getpixel((16, 16)), (91, 48, 44, 32))

    def test__validate_true(self):
        # Arrange
        prefix = b"DDS etc"

        # Act
        output = DdsImagePlugin._validate(prefix)

        # Assert
        self.assertTrue(output)

    def test__validate_false(self):
        # Arrange
        prefix = b"something invalid"

        # Act
        output = DdsImagePlugin._validate(prefix)

        # Assert
        self.assertFalse(output)


if __name__ == '__main__':
    unittest.main()

# End of file
