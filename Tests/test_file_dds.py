from io import BytesIO

from PIL import DdsImagePlugin, Image

from .helper import PillowTestCase

TEST_FILE_DXT1 = "Tests/images/dxt1-rgb-4bbp-noalpha_MipMaps-1.dds"
TEST_FILE_DXT3 = "Tests/images/dxt3-argb-8bbp-explicitalpha_MipMaps-1.dds"
TEST_FILE_DXT5 = "Tests/images/dxt5-argb-8bbp-interpolatedalpha_MipMaps-1.dds"
TEST_FILE_DX10_BC7 = "Tests/images/bc7-argb-8bpp_MipMaps-1.dds"
TEST_FILE_DX10_BC7_UNORM_SRGB = "Tests/images/DXGI_FORMAT_BC7_UNORM_SRGB.dds"
TEST_FILE_UNCOMPRESSED_RGB = "Tests/images/uncompressed_rgb.dds"


class TestFileDds(PillowTestCase):
    """Test DdsImagePlugin"""

    def test_sanity_dxt1(self):
        """Check DXT1 images can be opened"""
        with Image.open(TEST_FILE_DXT1.replace(".dds", ".png")) as target:
            target = target.convert("RGBA")
        with Image.open(TEST_FILE_DXT1) as im:
            im.load()

            self.assertEqual(im.format, "DDS")
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (256, 256))

            self.assert_image_equal(im, target)

    def test_sanity_dxt5(self):
        """Check DXT5 images can be opened"""

        with Image.open(TEST_FILE_DXT5) as im:
            im.load()

        self.assertEqual(im.format, "DDS")
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (256, 256))

        with Image.open(TEST_FILE_DXT5.replace(".dds", ".png")) as target:
            self.assert_image_equal(target, im)

    def test_sanity_dxt3(self):
        """Check DXT3 images can be opened"""

        with Image.open(TEST_FILE_DXT3.replace(".dds", ".png")) as target:
            with Image.open(TEST_FILE_DXT3) as im:
                im.load()

                self.assertEqual(im.format, "DDS")
                self.assertEqual(im.mode, "RGBA")
                self.assertEqual(im.size, (256, 256))

                self.assert_image_equal(target, im)

    def test_dx10_bc7(self):
        """Check DX10 images can be opened"""

        with Image.open(TEST_FILE_DX10_BC7) as im:
            im.load()

            self.assertEqual(im.format, "DDS")
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (256, 256))

            with Image.open(TEST_FILE_DX10_BC7.replace(".dds", ".png")) as target:
                self.assert_image_equal(target, im)

    def test_dx10_bc7_unorm_srgb(self):
        """Check DX10 unsigned normalized integer images can be opened"""

        with Image.open(TEST_FILE_DX10_BC7_UNORM_SRGB) as im:
            im.load()

            self.assertEqual(im.format, "DDS")
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (16, 16))
            self.assertEqual(im.info["gamma"], 1 / 2.2)

            with Image.open(
                TEST_FILE_DX10_BC7_UNORM_SRGB.replace(".dds", ".png")
            ) as target:
                self.assert_image_equal(target, im)

    def test_unimplemented_dxgi_format(self):
        self.assertRaises(
            NotImplementedError,
            Image.open,
            "Tests/images/unimplemented_dxgi_format.dds",
        )

    def test_uncompressed_rgb(self):
        """Check uncompressed RGB images can be opened"""

        with Image.open(TEST_FILE_UNCOMPRESSED_RGB) as im:
            im.load()

            self.assertEqual(im.format, "DDS")
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (800, 600))

            with Image.open(
                TEST_FILE_UNCOMPRESSED_RGB.replace(".dds", ".png")
            ) as target:
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
        with open(TEST_FILE_DXT5, "rb") as f:
            img_file = f.read()

        def short_header():
            Image.open(BytesIO(img_file[:119]))

        self.assertRaises(IOError, short_header)

    def test_short_file(self):
        """ Check that the appropriate error is thrown for a short file"""

        with open(TEST_FILE_DXT5, "rb") as f:
            img_file = f.read()

        def short_file():
            with Image.open(BytesIO(img_file[:-100])) as im:
                im.load()

        self.assertRaises(IOError, short_file)

    def test_unimplemented_pixel_format(self):
        self.assertRaises(
            NotImplementedError,
            Image.open,
            "Tests/images/unimplemented_pixel_format.dds",
        )
