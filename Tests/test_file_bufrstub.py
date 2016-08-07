from helper import unittest, PillowTestCase

from PIL import BufrStubImagePlugin


class TestFileBufrStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          BufrStubImagePlugin.BufrStubImageFile(invalid_file))


if __name__ == '__main__':
    unittest.main()
