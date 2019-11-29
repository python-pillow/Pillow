import unittest

from PIL import DcxImagePlugin, Image

from .helper import PillowTestCase, hopper, is_pypy

# Created with ImageMagick: convert hopper.ppm hopper.dcx
TEST_FILE = "Tests/images/hopper.dcx"


class TestFileDcx(PillowTestCase):
    def test_sanity(self):
        # Arrange

        # Act
        with Image.open(TEST_FILE) as im:

            # Assert
            self.assertEqual(im.size, (128, 128))
            self.assertIsInstance(im, DcxImagePlugin.DcxImageFile)
            orig = hopper()
            self.assert_image_equal(im, orig)

    @unittest.skipIf(is_pypy(), "Requires CPython")
    def test_unclosed_file(self):
        def open():
            im = Image.open(TEST_FILE)
            im.load()

        self.assert_warning(ResourceWarning, open)

    def test_closed_file(self):
        def open():
            im = Image.open(TEST_FILE)
            im.load()
            im.close()

        self.assert_warning(None, open)

    def test_context_manager(self):
        def open():
            with Image.open(TEST_FILE) as im:
                im.load()

        self.assert_warning(None, open)

    def test_invalid_file(self):
        with open("Tests/images/flower.jpg", "rb") as fp:
            self.assertRaises(SyntaxError, DcxImagePlugin.DcxImageFile, fp)

    def test_tell(self):
        # Arrange
        with Image.open(TEST_FILE) as im:

            # Act
            frame = im.tell()

            # Assert
            self.assertEqual(frame, 0)

    def test_n_frames(self):
        with Image.open(TEST_FILE) as im:
            self.assertEqual(im.n_frames, 1)
            self.assertFalse(im.is_animated)

    def test_eoferror(self):
        with Image.open(TEST_FILE) as im:
            n_frames = im.n_frames

            # Test seeking past the last frame
            self.assertRaises(EOFError, im.seek, n_frames)
            self.assertLess(im.tell(), n_frames)

            # Test that seeking to the last frame does not raise an error
            im.seek(n_frames - 1)

    def test_seek_too_far(self):
        # Arrange
        with Image.open(TEST_FILE) as im:
            frame = 999  # too big on purpose

        # Act / Assert
        self.assertRaises(EOFError, im.seek, frame)
