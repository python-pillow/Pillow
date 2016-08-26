from io import BytesIO

from helper import unittest, PillowTestCase
from PIL import Image, DdsImagePlugin

TEST_FILE_DXT1 = "Tests/images/dxt1-rgb-4bbp-noalpha_MipMaps-1.dds"
TEST_FILE_DXT3 = "Tests/images/dxt3-argb-8bbp-explicitalpha_MipMaps-1.dds"
TEST_FILE_DXT5 = "Tests/images/dxt5-argb-8bbp-interpolatedalpha_MipMaps-1.dds"
TEST_FILE_DX10_BC7 = "Tests/images/bc7-argb-8bpp_MipMaps-1.dds"


class TestFileDds(PillowTestCase):
    """Test DdsImagePlugin"""

    def test_sanity_dxt1(self):
        """Check DXT1 images can be opened"""
        target = Image.open(TEST_FILE_DXT1.replace('.dds', '.png'))

        im = Image.open(TEST_FILE_DXT1)
        im.load()

        self.assertEqual(im.format, "DDS")
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (256, 256))

        self.assert_image_equal(target.convert('RGBA'), im)

    def test_sanity_dxt5(self):
        """Check DXT5 images can be opened"""

        target = Image.open(TEST_FILE_DXT5.replace('.dds', '.png'))

        im = Image.open(TEST_FILE_DXT5)
        im.load()

        self.assertEqual(im.format, "DDS")
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (256, 256))

        self.assert_image_equal(target, im)

    def test_sanity_dxt3(self):
        """Check DXT3 images can be opened"""

        target = Image.open(TEST_FILE_DXT3.replace('.dds', '.png'))

        im = Image.open(TEST_FILE_DXT3)
        im.load()

        self.assertEqual(im.format, "DDS")
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (256, 256))

        self.assert_image_equal(target, im)

    def test_dx10_bc7(self):
        """Check DX10 images can be opened"""

        target = Image.open(TEST_FILE_DX10_BC7.replace('.dds', '.png'))

        im = Image.open(TEST_FILE_DX10_BC7)
        im.load()

        self.assertEqual(im.format, "DDS")
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (256, 256))

        self.assert_image_equal(target, im)

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

    def test_short_header(self):
        """ Check a short header"""
        with open(TEST_FILE_DXT5, 'rb') as f:
            img_file = f.read()

        def short_header():
            Image.open(BytesIO(img_file[:119]))

        self.assertRaises(IOError, short_header)

    def test_short_file(self):
        """ Check that the appropriate error is thrown for a short file"""

        with open(TEST_FILE_DXT5, 'rb') as f:
            img_file = f.read()

        def short_file():
            im = Image.open(BytesIO(img_file[:-100]))
            im.load()

        self.assertRaises(IOError, short_file)

if __name__ == '__main__':
    unittest.main()
