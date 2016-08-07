from helper import unittest, PillowTestCase

from PIL import GribStubImagePlugin


class TestFileGribStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          GribStubImagePlugin.GribStubImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
