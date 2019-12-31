from PIL import Image, XVThumbImagePlugin

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/hopper.p7"


class TestFileXVThumb(PillowTestCase):
    def test_open(self):
        # Act
        with Image.open(TEST_FILE) as im:

            # Assert
            self.assertEqual(im.format, "XVThumb")

            # Create a Hopper image with a similar XV palette
            im_hopper = hopper().quantize(palette=im)
            self.assert_image_similar(im, im_hopper, 9)

    def test_unexpected_eof(self):
        # Test unexpected EOF reading XV thumbnail file
        # Arrange
        bad_file = "Tests/images/hopper_bad.p7"

        # Act / Assert
        self.assertRaises(SyntaxError, XVThumbImagePlugin.XVThumbImageFile, bad_file)

    def test_invalid_file(self):
        # Arrange
        invalid_file = "Tests/images/flower.jpg"

        # Act / Assert
        self.assertRaises(
            SyntaxError, XVThumbImagePlugin.XVThumbImageFile, invalid_file
        )
