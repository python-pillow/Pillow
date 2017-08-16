from helper import unittest, PillowTestCase

from PIL import Image, FliImagePlugin

# created as an export of a palette image from Gimp2.6
# save as...-> hopper.fli, default options.
static_test_file = "Tests/images/hopper.fli"

# From https://samples.libav.org/fli-flc/
animated_test_file = "Tests/images/a.fli"


class TestFileFli(PillowTestCase):

    def test_sanity(self):
        im = Image.open(static_test_file)
        im.load()
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "FLI")
        self.assertFalse(im.is_animated)

        im = Image.open(animated_test_file)
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (320, 200))
        self.assertEqual(im.format, "FLI")
        self.assertEqual(im.info["duration"], 71)
        self.assertTrue(im.is_animated)

    def test_tell(self):
        # Arrange
        im = Image.open(static_test_file)

        # Act
        frame = im.tell()

        # Assert
        self.assertEqual(frame, 0)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: FliImagePlugin.FliImageFile(invalid_file))

    def test_n_frames(self):
        im = Image.open(static_test_file)
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

        im = Image.open(animated_test_file)
        self.assertEqual(im.n_frames, 384)
        self.assertTrue(im.is_animated)

    def test_eoferror(self):
        im = Image.open(animated_test_file)

        n_frames = im.n_frames
        while True:
            n_frames -= 1
            try:
                im.seek(n_frames)
                break
            except EOFError:
                self.assertLess(im.tell(), n_frames)

    def test_seek_outside(self):
        # Test negative seek
        im = Image.open(static_test_file)
        im.seek(-1)
        self.assertEqual(im.tell(), 0)

        # Test seek past end of file
        self.assertRaises(EOFError, lambda: im.seek(2))

    def test_seek_tell(self):
        im = Image.open(animated_test_file)

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


if __name__ == '__main__':
    unittest.main()
