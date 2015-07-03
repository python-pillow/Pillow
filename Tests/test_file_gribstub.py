from helper import unittest, PillowTestCase

from PIL import GribStubImagePlugin


class TestFileGribStub(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: GribStubImagePlugin.GribStubImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
