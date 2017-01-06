from PIL import FpxImagePlugin
from PIL.exceptions import InvalidFileType
from helper import unittest, PillowTestCase


class TestFileFpx(PillowTestCase):

    def test_invalid_file(self):
        # Test an invalid OLE file
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(InvalidFileType,
                          lambda: FpxImagePlugin.FpxImageFile(invalid_file))

        # Test a valid OLE file, but not an FPX file
        ole_file = "Tests/images/test-ole-file.doc"
        self.assertRaises(InvalidFileType,
                          lambda: FpxImagePlugin.FpxImageFile(ole_file))


if __name__ == '__main__':
    unittest.main()
