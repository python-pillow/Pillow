from helper import unittest, PillowTestCase, hopper

from PIL import Image

try:
    from PIL import _webp
    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


class TestFileWebpLossless(PillowTestCase):

    def setUp(self):
        if not HAVE_WEBP:
            self.skipTest('WebP support not installed')
            return

        if _webp.WebPDecoderVersion() < 0x0200:
            self.skipTest('lossless not included')

        self.rgb_mode = "RGB"

    def test_write_lossless_rgb(self):
        temp_file = self.tempfile("temp.webp")

        hopper(self.rgb_mode).save(temp_file, lossless=True)

        image = Image.open(temp_file)
        image.load()

        self.assertEqual(image.mode, self.rgb_mode)
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        self.assert_image_equal(image, hopper(self.rgb_mode))


if __name__ == '__main__':
    unittest.main()
