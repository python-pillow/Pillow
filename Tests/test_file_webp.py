from helper import unittest, PillowTestCase, hopper

from PIL import Image

try:
    from PIL import _webp
    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


class TestFileWebp(PillowTestCase):

    def setUp(self):
        if not HAVE_WEBP:
            self.skipTest('WebP support not installed')
            return

        # WebPAnimDecoder only returns RGBA or RGBX, never RGB
        self.rgb_mode = "RGBX" if _webp.HAVE_WEBPANIM else "RGB"

    def test_version(self):
        _webp.WebPDecoderVersion()
        _webp.WebPDecoderBuggyAlpha()

    def test_read_rgb(self):
        """
        Can we read a RGB mode WebP file without error?
        Does it have the bits we expect?
        """

        file_path = "Tests/images/hopper.webp"
        image = Image.open(file_path)

        self.assertEqual(image.mode, self.rgb_mode)
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        # generated with:
        # dwebp -ppm ../../Tests/images/hopper.webp -o hopper_webp_bits.ppm
        target = Image.open('Tests/images/hopper_webp_bits.ppm')
        target = target.convert(self.rgb_mode)
        self.assert_image_similar(image, target, 20.0)

    def test_write_rgb(self):
        """
        Can we write a RGB mode file to webp without error.
        Does it have the bits we expect?
        """

        temp_file = self.tempfile("temp.webp")

        hopper(self.rgb_mode).save(temp_file)
        image = Image.open(temp_file)

        self.assertEqual(image.mode, self.rgb_mode)
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        # If we're using the exact same version of WebP, this test should pass.
        # but it doesn't if the WebP is generated on Ubuntu and tested on
        # Fedora.

        # generated with: dwebp -ppm temp.webp -o hopper_webp_write.ppm
        # target = Image.open('Tests/images/hopper_webp_write.ppm')
        # self.assert_image_equal(image, target)

        # This test asserts that the images are similar. If the average pixel
        # difference between the two images is less than the epsilon value,
        # then we're going to accept that it's a reasonable lossy version of
        # the image. The old lena images for WebP are showing ~16 on
        # Ubuntu, the jpegs are showing ~18.
        target = hopper(self.rgb_mode)
        self.assert_image_similar(image, target, 12.0)

    def test_write_unsupported_mode_L(self):
        """
        Saving a black-and-white file to WebP format should work, and be
        similar to the original file.
        """

        temp_file = self.tempfile("temp.webp")
        hopper("L").save(temp_file)
        image = Image.open(temp_file)

        self.assertEqual(image.mode, self.rgb_mode)
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")

        image.load()
        image.getdata()
        target = hopper("L").convert(self.rgb_mode)

        self.assert_image_similar(image, target, 10.0)

    def test_write_unsupported_mode_P(self):
        """
        Saving a palette-based file to WebP format should work, and be
        similar to the original file.
        """

        temp_file = self.tempfile("temp.webp")
        hopper("P").save(temp_file)
        image = Image.open(temp_file)

        self.assertEqual(image.mode, self.rgb_mode)
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")

        image.load()
        image.getdata()
        target = hopper("P").convert(self.rgb_mode)

        self.assert_image_similar(image, target, 50.0)

    def test_WebPEncode_with_invalid_args(self):
        """
        Calling encoder functions with no arguments should result in an error.
        """

        if _webp.HAVE_WEBPANIM:
            self.assertRaises(TypeError, _webp.WebPAnimEncoder)
        self.assertRaises(TypeError, _webp.WebPEncode)

    def test_WebPDecode_with_invalid_args(self):
        """
        Calling decoder functions with no arguments should result in an error.
        """

        if _webp.HAVE_WEBPANIM:
            self.assertRaises(TypeError, _webp.WebPAnimDecoder)
        self.assertRaises(TypeError, _webp.WebPDecode)


if __name__ == '__main__':
    unittest.main()
