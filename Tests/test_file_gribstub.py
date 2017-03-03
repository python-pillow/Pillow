from helper import unittest, PillowTestCase, hopper

from PIL import GribStubImagePlugin


class TestFileGribStub(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda:
                          GribStubImagePlugin.GribStubImageFile(invalid_file))

    def test_save(self):
        im = hopper()

        tmpfile = self.tempfile("temp.grib")
        self.assertRaises(IOError, lambda: im.save(tmpfile))


if __name__ == '__main__':
    unittest.main()
