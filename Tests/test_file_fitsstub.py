from helper import unittest, PillowTestCase

from PIL import FitsStubImagePlugin


class TestFileFitsStub(PillowTestCase):

    def test_invalid_file(self):
        self.assertRaises(SyntaxError, lambda: FitsStubImagePlugin.FITSStubImageFile("Tests/images/flower.jpg"))


if __name__ == '__main__':
    unittest.main()

# End of file
