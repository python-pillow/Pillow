import unittest

from PIL import Image, PsdImagePlugin

from .helper import PillowTestCase, hopper, is_pypy

test_file = "Tests/images/hopper.psd"


class TestImagePsd(PillowTestCase):
    def test_sanity(self):
        with Image.open(test_file) as im:
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "PSD")

            im2 = hopper()
            self.assert_image_similar(im, im2, 4.8)

    @unittest.skipIf(is_pypy(), "Requires CPython")
    def test_unclosed_file(self):
        def open():
            im = Image.open(test_file)
            im.load()

        self.assert_warning(ResourceWarning, open)

    def test_closed_file(self):
        def open():
            im = Image.open(test_file)
            im.load()
            im.close()

        self.assert_warning(None, open)

    def test_context_manager(self):
        def open():
            with Image.open(test_file) as im:
                im.load()

        self.assert_warning(None, open)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError, PsdImagePlugin.PsdImageFile, invalid_file)

    def test_n_frames(self):
        with Image.open("Tests/images/hopper_merged.psd") as im:
            self.assertEqual(im.n_frames, 1)
            self.assertFalse(im.is_animated)

        with Image.open(test_file) as im:
            self.assertEqual(im.n_frames, 2)
            self.assertTrue(im.is_animated)

    def test_eoferror(self):
        with Image.open(test_file) as im:
            # PSD seek index starts at 1 rather than 0
            n_frames = im.n_frames + 1

            # Test seeking past the last frame
            self.assertRaises(EOFError, im.seek, n_frames)
            self.assertLess(im.tell(), n_frames)

            # Test that seeking to the last frame does not raise an error
            im.seek(n_frames - 1)

    def test_seek_tell(self):
        with Image.open(test_file) as im:

            layer_number = im.tell()
            self.assertEqual(layer_number, 1)

            self.assertRaises(EOFError, im.seek, 0)

            im.seek(1)
            layer_number = im.tell()
            self.assertEqual(layer_number, 1)

            im.seek(2)
            layer_number = im.tell()
            self.assertEqual(layer_number, 2)

    def test_seek_eoferror(self):
        with Image.open(test_file) as im:

            self.assertRaises(EOFError, im.seek, -1)

    def test_open_after_exclusive_load(self):
        with Image.open(test_file) as im:
            im.load()
            im.seek(im.tell() + 1)
            im.load()

    def test_icc_profile(self):
        with Image.open(test_file) as im:
            self.assertIn("icc_profile", im.info)

            icc_profile = im.info["icc_profile"]
            self.assertEqual(len(icc_profile), 3144)

    def test_no_icc_profile(self):
        with Image.open("Tests/images/hopper_merged.psd") as im:
            self.assertNotIn("icc_profile", im.info)

    def test_combined_larger_than_size(self):
        # The 'combined' sizes of the individual parts is larger than the
        # declared 'size' of the extra data field, resulting in a backwards seek.

        # If we instead take the 'size' of the extra data field as the source of truth,
        # then the seek can't be negative
        with self.assertRaises(IOError):
            Image.open("Tests/images/combined_larger_than_size.psd")
