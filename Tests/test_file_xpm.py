from helper import unittest, PillowTestCase

from PIL import Image

# sample ppm stream
TEST_FILE = "Tests/images/lena.xpm"


class TestFileXpm(PillowTestCase):

    def test_sanity(self):
        im = Image.open(TEST_FILE)
        im.load()
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "XPM")

    def test_load_read(self):
        # Arrange
        im = Image.open(TEST_FILE)
        dummy_bytes = 1

        # Act
        data = im.load_read(dummy_bytes)

        # Assert
        self.assertEqual(len(data), 16384)


if __name__ == '__main__':
    unittest.main()

# End of file
