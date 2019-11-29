import unittest

from PIL import FliImagePlugin, Image

from .helper import PillowTestCase, is_pypy

# created as an export of a palette image from Gimp2.6
# save as...-> hopper.fli, default options.
static_test_file = "Tests/images/hopper.fli"

# From https://samples.libav.org/fli-flc/
animated_test_file = "Tests/images/a.fli"


class TestFileFli(PillowTestCase):
    def test_sanity(self):
        with Image.open(static_test_file) as im:
            im.load()
            self.assertEqual(im.mode, "P")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "FLI")
            self.assertFalse(im.is_animated)

        with Image.open(animated_test_file) as im:
            self.assertEqual(im.mode, "P")
            self.assertEqual(im.size, (320, 200))
            self.assertEqual(im.format, "FLI")
            self.assertEqual(im.info["duration"], 71)
            self.assertTrue(im.is_animated)

    @unittest.skipIf(is_pypy(), "Requires CPython")
    def test_unclosed_file(self):
        def open():
            im = Image.open(static_test_file)
            im.load()

        self.assert_warning(ResourceWarning, open)

    def test_closed_file(self):
        def open():
            im = Image.open(static_test_file)
            im.load()
            im.close()

        self.assert_warning(None, open)

    def test_context_manager(self):
        def open():
            with Image.open(static_test_file) as im:
                im.load()

        self.assert_warning(None, open)

    def test_tell(self):
        # Arrange
        with Image.open(static_test_file) as im:

            # Act
            frame = im.tell()

            # Assert
            self.assertEqual(frame, 0)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, FliImagePlugin.FliImageFile, invalid_file)

    def test_n_frames(self):
        with Image.open(static_test_file) as im:
            self.assertEqual(im.n_frames, 1)
            self.assertFalse(im.is_animated)

        with Image.open(animated_test_file) as im:
            self.assertEqual(im.n_frames, 384)
            self.assertTrue(im.is_animated)

    def test_eoferror(self):
        with Image.open(animated_test_file) as im:
            n_frames = im.n_frames

            # Test seeking past the last frame
            self.assertRaises(EOFError, im.seek, n_frames)
            self.assertLess(im.tell(), n_frames)

            # Test that seeking to the last frame does not raise an error
            im.seek(n_frames - 1)

    def test_seek_tell(self):
        with Image.open(animated_test_file) as im:

            layer_number = im.tell()
            self.assertEqual(layer_number, 0)

            im.seek(0)
            layer_number = im.tell()
            self.assertEqual(layer_number, 0)

            im.seek(1)
            layer_number = im.tell()
            self.assertEqual(layer_number, 1)

            im.seek(2)
            layer_number = im.tell()
            self.assertEqual(layer_number, 2)

            im.seek(1)
            layer_number = im.tell()
            self.assertEqual(layer_number, 1)

    def test_seek(self):
        with Image.open(animated_test_file) as im:
            im.seek(50)

            with Image.open("Tests/images/a_fli.png") as expected:
                self.assert_image_equal(im, expected)
