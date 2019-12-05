from PIL import Image, PixarImagePlugin

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/hopper.pxr"


class TestFilePixar(PillowTestCase):
    def test_sanity(self):
        with Image.open(TEST_FILE) as im:
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "PIXAR")
            self.assertIsNone(im.get_format_mimetype())

            im2 = hopper()
            self.assert_image_similar(im, im2, 4.8)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, PixarImagePlugin.PixarImageFile, invalid_file)
