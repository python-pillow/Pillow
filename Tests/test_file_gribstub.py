from PIL import GribStubImagePlugin
from PIL.exceptions import InvalidFileType
from helper import unittest, PillowTestCase


class TestFileGribStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(InvalidFileType,
                          lambda:
                          GribStubImagePlugin.GribStubImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
