from PIL import BufrStubImagePlugin
from PIL.exceptions import InvalidFileType
from helper import unittest, PillowTestCase


class TestFileBufrStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(InvalidFileType,
                          lambda:
                          BufrStubImagePlugin.BufrStubImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
