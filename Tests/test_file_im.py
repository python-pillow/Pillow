import unittest

from PIL import Image, ImImagePlugin

from .helper import PillowTestCase, hopper, is_pypy

# sample im
TEST_IM = "Tests/images/hopper.im"


class TestFileIm(PillowTestCase):
    def test_sanity(self):
        with Image.open(TEST_IM) as im:
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "IM")

    @unittest.skipIf(is_pypy(), "Requires CPython")
    def test_unclosed_file(self):
        def open():
            im = Image.open(TEST_IM)
            im.load()

        self.assert_warning(ResourceWarning, open)

    def test_closed_file(self):
        def open():
            im = Image.open(TEST_IM)
            im.load()
            im.close()

        self.assert_warning(None, open)

    def test_context_manager(self):
        def open():
            with Image.open(TEST_IM) as im:
                im.load()

        self.assert_warning(None, open)

    def test_tell(self):
        # Arrange
        with Image.open(TEST_IM) as im:

            # Act
            frame = im.tell()

        # Assert
        self.assertEqual(frame, 0)

    def test_n_frames(self):
        with Image.open(TEST_IM) as im:
            self.assertEqual(im.n_frames, 1)
            self.assertFalse(im.is_animated)

    def test_eoferror(self):
        with Image.open(TEST_IM) as im:
            n_frames = im.n_frames

            # Test seeking past the last frame
            self.assertRaises(EOFError, im.seek, n_frames)
            self.assertLess(im.tell(), n_frames)

            # Test that seeking to the last frame does not raise an error
            im.seek(n_frames - 1)

    def test_roundtrip(self):
        for mode in ["RGB", "P", "PA"]:
            out = self.tempfile("temp.im")
            im = hopper(mode)
            im.save(out)
            with Image.open(out) as reread:

                self.assert_image_equal(reread, im)

    def test_save_unsupported_mode(self):
        out = self.tempfile("temp.im")
        im = hopper("HSV")
        self.assertRaises(ValueError, im.save, out)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, ImImagePlugin.ImImageFile, invalid_file)

    def test_number(self):
        self.assertEqual(1.2, ImImagePlugin.number("1.2"))
