from helper import unittest, PillowTestCase, hopper

from PIL import GribStubImagePlugin, Image

TEST_FILE = "Tests/images/WAlaska.wind.7days.grb"


class TestFileGribStub(PillowTestCase):

    def test_open(self):
        # Act
        im = Image.open(TEST_FILE)

        # Assert
        self.assertEqual(im.format, "GRIB")

        # Dummy data from the stub
        self.assertEqual(im.mode, "F")
        self.assertEqual(im.size, (1, 1))

    def test_invalid_file(self):
        # Arrange
        invalid_file = "Tests/images/flower.jpg"

        # Act / Assert
        self.assertRaises(SyntaxError,
                          GribStubImagePlugin.GribStubImageFile, invalid_file)

    def test_load(self):
        # Arrange
        im = Image.open(TEST_FILE)

        # Act / Assert: stub cannot load without an implemented handler
        self.assertRaises(IOError, im.load)

    def test_save(self):
        # Arrange
        im = hopper()
        tmpfile = self.tempfile("temp.grib")

        # Act / Assert: stub cannot save without an implemented handler
        self.assertRaises(IOError, im.save, tmpfile)


if __name__ == '__main__':
    unittest.main()
