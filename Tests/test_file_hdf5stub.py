from helper import unittest, PillowTestCase

from PIL import Hdf5StubImagePlugin


class TestFileHdf5Stub(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: Hdf5StubImagePlugin.HDF5StubImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
