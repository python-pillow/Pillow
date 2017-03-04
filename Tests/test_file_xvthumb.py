from helper import hopper, unittest, PillowTestCase

from PIL import Image, XVThumbImagePlugin

TEST_FILE = "Tests/images/hopper.p7"


class TestFileXVThumb(PillowTestCase):

    def test_open(self):
        # Act
        im = Image.open(TEST_FILE)

        # Assert
        self.assertEqual(im.format, "XVThumb")
        self.assert_image_similar(im, hopper("P"), 49)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          XVThumbImagePlugin.XVThumbImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
