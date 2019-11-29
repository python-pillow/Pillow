import unittest

from PIL import Image, ImagePalette, features

from .helper import PillowTestCase, hopper

try:
    from PIL import MicImagePlugin
except ImportError:
    olefile_installed = False
else:
    olefile_installed = True

TEST_FILE = "Tests/images/hopper.mic"


@unittest.skipUnless(olefile_installed, "olefile package not installed")
@unittest.skipUnless(features.check("libtiff"), "libtiff not installed")
class TestFileMic(PillowTestCase):
    def test_sanity(self):
        with Image.open(TEST_FILE) as im:
            im.load()
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "MIC")

            # Adjust for the gamma of 2.2 encoded into the file
            lut = ImagePalette.make_gamma_lut(1 / 2.2)
            im = Image.merge("RGBA", [chan.point(lut) for chan in im.split()])

            im2 = hopper("RGBA")
            self.assert_image_similar(im, im2, 10)

    def test_n_frames(self):
        with Image.open(TEST_FILE) as im:

            self.assertEqual(im.n_frames, 1)

    def test_is_animated(self):
        with Image.open(TEST_FILE) as im:

            self.assertFalse(im.is_animated)

    def test_tell(self):
        with Image.open(TEST_FILE) as im:

            self.assertEqual(im.tell(), 0)

    def test_seek(self):
        with Image.open(TEST_FILE) as im:

            im.seek(0)
            self.assertEqual(im.tell(), 0)

            self.assertRaises(EOFError, im.seek, 99)
            self.assertEqual(im.tell(), 0)

    def test_invalid_file(self):
        # Test an invalid OLE file
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(SyntaxError, MicImagePlugin.MicImageFile, invalid_file)

        # Test a valid OLE file, but not a MIC file
        ole_file = "Tests/images/test-ole-file.doc"
        self.assertRaises(SyntaxError, MicImagePlugin.MicImageFile, ole_file)
