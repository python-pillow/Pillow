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

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError,
                              DcxImagePlugin.DcxImageFile, fp)

    def test_tell(self):
        # Arrange
        im = Image.open(TEST_FILE)

        # Act
        frame = im.tell()

        # Assert
        self.assertEqual(frame, 0)

    def test_n_frames(self):
        im = Image.open(TEST_FILE)
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

    def test_eoferror(self):
        im = Image.open(TEST_FILE)
        n_frames = im.n_frames

        # Test seeking past the last frame
        self.assertRaises(EOFError, im.seek, n_frames)
        self.assertLess(im.tell(), n_frames)

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames-1)

    def test_seek_too_far(self):
        # Arrange
        im = Image.open(TEST_FILE)
        frame = 999  # too big on purpose

        # Act / Assert
        self.assertRaises(EOFError, im.seek, frame)


if __name__ == '__main__':
    unittest.main()
