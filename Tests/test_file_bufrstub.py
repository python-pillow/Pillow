from helper import unittest, PillowTestCase

from PIL import BufrStubImagePlugin


class TestFileBufrStub(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: BufrStubImagePlugin.BufrStubImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
