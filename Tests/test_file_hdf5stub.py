from PIL import Hdf5StubImagePlugin
from PIL.exceptions import InvalidFileType
from helper import unittest, PillowTestCase


class TestFileHdf5Stub(PillowTestCase):

    def test_invalid_file(self):
        test_file = "Tests/images/flower.jpg"

        self.assertRaises(InvalidFileType,
                          lambda:
                          Hdf5StubImagePlugin.HDF5StubImageFile(test_file))


if __name__ == '__main__':
    unittest.main()
