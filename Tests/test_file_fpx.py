from helper import unittest, PillowTestCase

from PIL import FpxImagePlugin


class TestFileFpx(PillowTestCase):

    def test_invalid_file(self):
        # Test an invalid OLE file
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(SyntaxError,
                          lambda: FpxImagePlugin.FpxImageFile(invalid_file))

        # Test a valid OLE file, but not an FPX file
        ole_file = "Tests/images/test-ole-file.doc"
        self.assertRaises(SyntaxError,
                          lambda: FpxImagePlugin.FpxImageFile(ole_file))


if __name__ == '__main__':
    unittest.main()
