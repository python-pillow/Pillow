from helper import unittest, PillowTestCase

from PIL import MicImagePlugin


class TestFileMic(PillowTestCase):

    def test_invalid_file(self):
        # Test an invalid OLE file
        invalid_file = "Tests/images/flower.jpg"
        self.assertRaises(SyntaxError,
                          lambda: MicImagePlugin.MicImageFile(invalid_file))

        # Test a valid OLE file, but not a MIC file
        ole_file = "Tests/images/test-ole-file.doc"
        self.assertRaises(SyntaxError,
                          lambda: MicImagePlugin.MicImageFile(ole_file))


if __name__ == '__main__':
    unittest.main()
