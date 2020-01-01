import unittest

from PIL import Image

from .helper import PillowTestCase

try:
    from PIL import FpxImagePlugin
except ImportError:
    olefile_installed = False
else:
    olefile_installed = True


@unittest.skipUnless(olefile_installed, "olefile package not installed")
class TestFileFpx(PillowTestCase):
    def test_invalid_file(self):
        # Test an invalid OLE file
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(SyntaxError, FpxImagePlugin.FpxImageFile, invalid_file)

        # Test a valid OLE file, but not an FPX file
        ole_file = "Tests/images/test-ole-file.doc"
        self.assertRaises(SyntaxError, FpxImagePlugin.FpxImageFile, ole_file)

    def test_fpx_invalid_number_of_bands(self):
        with self.assertRaisesRegex(IOError, "Invalid number of bands"):
            Image.open("Tests/images/input_bw_five_bands.fpx")
