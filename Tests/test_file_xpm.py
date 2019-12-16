from PIL import Image, XpmImagePlugin

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/hopper.xpm"


class TestFileXpm(PillowTestCase):
    def test_sanity(self):
        with Image.open(TEST_FILE) as im:
            im.load()
            self.assertEqual(im.mode, "P")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "XPM")

            # large error due to quantization->44 colors.
            self.assert_image_similar(im.convert("RGB"), hopper("RGB"), 60)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, XpmImagePlugin.XpmImageFile, invalid_file)

    def test_load_read(self):
        # Arrange
        with Image.open(TEST_FILE) as im:
            dummy_bytes = 1

            # Act
            data = im.load_read(dummy_bytes)

        # Assert
        self.assertEqual(len(data), 16384)
