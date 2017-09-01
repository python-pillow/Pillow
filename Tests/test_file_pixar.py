from helper import hopper, unittest, PillowTestCase

from PIL import Image, PixarImagePlugin

TEST_FILE = "Tests/images/hopper.pxr"


class TestFilePixar(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_FILE)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "PIXAR")

        im2 = hopper()
        self.assert_image_similar(im, im2, 4.8)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(
            SyntaxError,
            PixarImagePlugin.PixarImageFile, invalid_file)


if __name__ == '__main__':
    unittest.main()
