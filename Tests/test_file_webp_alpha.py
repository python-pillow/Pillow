from helper import unittest, PillowTestCase, hopper

from PIL import Image

try:
    from PIL import _webp
except ImportError:
    pass
    # Skip in setUp()


class TestFileWebpAlpha(PillowTestCase):

    def setUp(self):
        try:
            from PIL import _webp
        except ImportError:
            self.skipTest('WebP support not installed')

        if _webp.WebPDecoderBuggyAlpha(self):
            self.skipTest("Buggy early version of WebP installed, "
                          "not testing transparency")

    def test_read_rgba(self):
        # Generated with `cwebp transparent.png -o transparent.webp`
        file_path = "Tests/images/transparent.webp"
        image = Image.open(file_path)

        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (200, 150))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        image.tobytes()

        target = Image.open('Tests/images/transparent.png')
        self.assert_image_similar(image, target, 20.0)

    def test_write_lossless_rgb(self):
        temp_file = self.tempfile("temp.webp")
        # temp_file = "temp.webp"

        pil_image = hopper('RGBA')

        mask = Image.new("RGBA", (64, 64), (128, 128, 128, 128))
        # Add some partially transparent bits:
        pil_image.paste(mask, (0, 0), mask)

        pil_image.save(temp_file, lossless=True)

        image = Image.open(temp_file)
        image.load()

        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, pil_image.size)
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        self.assert_image_equal(image, pil_image)

    def test_write_rgba(self):
        """
        Can we write a RGBA mode file to webp without error.
        Does it have the bits we expect?
        """

        temp_file = self.tempfile("temp.webp")

        pil_image = Image.new("RGBA", (10, 10), (255, 0, 0, 20))
        pil_image.save(temp_file)

        if _webp.WebPDecoderBuggyAlpha(self):
            return

        image = Image.open(temp_file)
        image.load()

        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (10, 10))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        # early versions of webp are known to produce higher deviations:
        # deal with it
        if _webp.WebPDecoderVersion(self) <= 0x201:
            self.assert_image_similar(image, pil_image, 3.0)
        else:
            self.assert_image_similar(image, pil_image, 1.0)


if __name__ == '__main__':
    unittest.main()

# End of file
