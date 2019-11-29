from PIL import GribStubImagePlugin, Image

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/WAlaska.wind.7days.grb"


class TestFileGribStub(PillowTestCase):
    def test_open(self):
        # Act
        with Image.open(TEST_FILE) as im:

            # Assert
            self.assertEqual(im.format, "GRIB")

            # Dummy data from the stub
            self.assertEqual(im.mode, "F")
            self.assertEqual(im.size, (1, 1))

    def test_invalid_file(self):
        # Arrange
        invalid_file = "Tests/images/flower.jpg"

        # Act / Assert
        self.assertRaises(
            SyntaxError, GribStubImagePlugin.GribStubImageFile, invalid_file
        )

    def test_load(self):
        # Arrange
        with Image.open(TEST_FILE) as im:

            # Act / Assert: stub cannot load without an implemented handler
            self.assertRaises(IOError, im.load)

    def test_save(self):
        # Arrange
        im = hopper()
        tmpfile = self.tempfile("temp.grib")

        # Act / Assert: stub cannot save without an implemented handler
        self.assertRaises(IOError, im.save, tmpfile)
