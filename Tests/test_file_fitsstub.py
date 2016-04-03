from helper import unittest, PillowTestCase

from PIL import FitsStubImagePlugin


class TestFileFitsStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          FitsStubImagePlugin.FITSStubImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()

# End of file
