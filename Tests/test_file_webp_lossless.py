from helper import unittest, PillowTestCase, tearDownModule, lena

from PIL import Image

try:
    from PIL import _webp
except:
    pass
    # Skip in setUp()


class TestFileWebpLossless(PillowTestCase):

    def setUp(self):
        try:
            from PIL import _webp
        except:
            self.skipTest('WebP support not installed')

        if (_webp.WebPDecoderVersion() < 0x0200):
            self.skipTest('lossless not included')

    def test_write_lossless_rgb(self):
        temp_file = self.tempfile("temp.webp")

        lena("RGB").save(temp_file, lossless=True)

        image = Image.open(temp_file)
        image.load()

        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        self.assert_image_equal(image, lena("RGB"))


if __name__ == '__main__':
    unittest.main()

# End of file
