from helper import unittest, PillowTestCase, hopper

from PIL import Image, ImageFile, MspImagePlugin

import os

TEST_FILE = "Tests/images/hopper.msp"
EXTRA_DIR = "Tests/images/picins"


class TestFileMsp(PillowTestCase):

    def test_sanity(self):
        file = self.tempfile("temp.msp")

        hopper("1").save(file)

        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "1")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "MSP")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: MspImagePlugin.MspImageFile(invalid_file))

    def test_bad_checksum(self):
        # Arrange
        # This was created by forcing Pillow to save with checksum=0
        bad_checksum = "Tests/images/hopper_bad_checksum.msp"

        # Act / Assert
        self.assertRaises(SyntaxError,
                          lambda: MspImagePlugin.MspImageFile(bad_checksum))

    def test_open_windows_v1(self):
        # Arrange
        # Act
        im = Image.open(TEST_FILE)

        # Assert
        self.assert_image_equal(im, hopper("1"))
        self.assertIsInstance(im, MspImagePlugin.MspImageFile)

    @unittest.skipIf(not os.path.exists(EXTRA_DIR),
                     "Extra image files not installed")
    def test_open_windows_v2(self):
        # Arrange
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        files = (os.path.join(EXTRA_DIR, f) for f in os.listdir(EXTRA_DIR)
                 if os.path.splitext(f)[1] == '.msp')
        for path in files:

            # Act
            with Image.open(path) as im:
                im.load()

                # Assert
                self.assertEqual(im.mode, "1")
                self.assertGreater(im.size, (360, 332))
                self.assertIsInstance(im, MspImagePlugin.MspImageFile)
                if "mandel" in path:
                    self.assertEqual(im.getpixel((0, 0)), 0)
                elif "mexhat" in path:
                    self.assertEqual(im.getpixel((0, 0)), 255)
                self.assertEqual(im.getpixel((200, 25)), 255)
        ImageFile.LOAD_TRUNCATED_IMAGES = False

    def test_cannot_save_wrong_mode(self):
        # Arrange
        im = hopper()
        filename = self.tempfile("temp.msp")

        # Act/Assert
        self.assertRaises(IOError, lambda: im.save(filename))


if __name__ == '__main__':
    unittest.main()
