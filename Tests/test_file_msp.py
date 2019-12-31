import os
import unittest

from PIL import Image, MspImagePlugin

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/hopper.msp"
EXTRA_DIR = "Tests/images/picins"
YA_EXTRA_DIR = "Tests/images/msp"


class TestFileMsp(PillowTestCase):
    def test_sanity(self):
        test_file = self.tempfile("temp.msp")

        hopper("1").save(test_file)

        with Image.open(test_file) as im:
            im.load()
            self.assertEqual(im.mode, "1")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "MSP")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, MspImagePlugin.MspImageFile, invalid_file)

    def test_bad_checksum(self):
        # Arrange
        # This was created by forcing Pillow to save with checksum=0
        bad_checksum = "Tests/images/hopper_bad_checksum.msp"

        # Act / Assert
        self.assertRaises(SyntaxError, MspImagePlugin.MspImageFile, bad_checksum)

    def test_open_windows_v1(self):
        # Arrange
        # Act
        with Image.open(TEST_FILE) as im:

            # Assert
            self.assert_image_equal(im, hopper("1"))
            self.assertIsInstance(im, MspImagePlugin.MspImageFile)

    def _assert_file_image_equal(self, source_path, target_path):
        with Image.open(source_path) as im:
            with Image.open(target_path) as target:
                self.assert_image_equal(im, target)

    @unittest.skipUnless(os.path.exists(EXTRA_DIR), "Extra image files not installed")
    def test_open_windows_v2(self):

        files = (
            os.path.join(EXTRA_DIR, f)
            for f in os.listdir(EXTRA_DIR)
            if os.path.splitext(f)[1] == ".msp"
        )
        for path in files:
            self._assert_file_image_equal(path, path.replace(".msp", ".png"))

    @unittest.skipIf(
        not os.path.exists(YA_EXTRA_DIR), "Even More Extra image files not installed"
    )
    def test_msp_v2(self):
        for f in os.listdir(YA_EXTRA_DIR):
            if ".MSP" not in f:
                continue
            path = os.path.join(YA_EXTRA_DIR, f)
            self._assert_file_image_equal(path, path.replace(".MSP", ".png"))

    def test_cannot_save_wrong_mode(self):
        # Arrange
        im = hopper()
        filename = self.tempfile("temp.msp")

        # Act/Assert
        self.assertRaises(IOError, im.save, filename)
