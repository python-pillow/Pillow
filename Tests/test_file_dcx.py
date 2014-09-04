from helper import unittest, PillowTestCase, hopper

from PIL import Image, DcxImagePlugin

# Created with ImageMagick: convert hopper.ppm hopper.dcx
TEST_FILE = "Tests/images/hopper.dcx"


class TestFileDcx(PillowTestCase):

    def test_sanity(self):
        # Arrange

        # Act
        im = Image.open(TEST_FILE)

        # Assert
        self.assertEqual(im.size, (128, 128))
        self.assertIsInstance(im, DcxImagePlugin.DcxImageFile)
        orig = hopper()
        self.assert_image_equal(im, orig)

    def test_tell(self):
        # Arrange
        im = Image.open(TEST_FILE)

        # Act
        frame = im.tell()

        # Assert
        self.assertEqual(frame, 0)

    def test_seek_too_far(self):
        # Arrange
        im = Image.open(TEST_FILE)
        frame = 999  # too big on purpose

        # Act / Assert
        self.assertRaises(EOFError, lambda: im.seek(frame))


if __name__ == '__main__':
    unittest.main()

# End of file
