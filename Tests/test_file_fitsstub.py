from helper import unittest, PillowTestCase

from PIL import FitsStubImagePlugin
from PIL.exceptions import InvalidFileType


class TestFileFitsStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(InvalidFileType,
                          lambda:
                          FitsStubImagePlugin.FITSStubImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
