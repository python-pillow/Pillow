from helper import unittest, PillowTestCase

from PIL import Image, DdsImagePlugin

TEST_FILE_DXT1 = "Tests/images/dxt1-rgb-4bbp-noalpha_MipMaps-1.dds"
TEST_FILE_DXT3 = "Tests/images/dxt3-argb-8bbp-explicitalpha_MipMaps-1.dds"
TEST_FILE_DXT5 = "Tests/images/dxt5-argb-8bbp-interpolatedalpha_MipMaps-1.dds"


class TestFileDds(PillowTestCase):
    """Test DdsImagePlugin"""

    def test_sanity_dxt1(self):
        """Check DXT1 images can be opened"""
        im = Image.open(TEST_FILE_DXT1)

        self.assertEqual(im.format, "DDS")
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (256, 256))
        self.assertIsInstance(im, DdsImagePlugin.DdsImageFile)

    def test_sanity_dxt5(self):
        """Check DXT5 images can be opened"""
        im = Image.open(TEST_FILE_DXT5)

        self.assertEqual(im.format, "DDS")
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (256, 256))
        self.assertIsInstance(im, DdsImagePlugin.DdsImageFile)

    def test_sanity_dxt3(self):
        """Check DXT3 images are not supported"""
        self.assertRaises(NotImplementedError,
                          lambda: Image.open(TEST_FILE_DXT3))

    def test__validate_true(self):
        """Check valid prefix"""
        # Arrange
        prefix = b"DDS etc"

        # Act
        output = DdsImagePlugin._validate(prefix)

        # Assert
        self.assertTrue(output)

    def test__validate_false(self):
        """Check invalid prefix"""
        # Arrange
        prefix = b"something invalid"

        # Act
        output = DdsImagePlugin._validate(prefix)

        # Assert
        self.assertFalse(output)


if __name__ == '__main__':
    unittest.main()

# End of file
