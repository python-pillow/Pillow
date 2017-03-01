from helper import unittest, PillowTestCase, hopper

from PIL import BufrStubImagePlugin


class TestFileBufrStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          BufrStubImagePlugin.BufrStubImageFile(invalid_file))

    def test_save(self):
        im = hopper()

        tmpfile = self.tempfile("temp.bufr")
        self.assertRaises(IOError, lambda: im.save(tmpfile))


if __name__ == '__main__':
    unittest.main()
