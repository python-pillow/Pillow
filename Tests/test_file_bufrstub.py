from PIL import BufrStubImagePlugin, Image

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/gfs.t06z.rassda.tm00.bufr_d"


class TestFileBufrStub(PillowTestCase):
    def test_open(self):
        # Act
        with Image.open(TEST_FILE) as im:

            # Assert
            self.assertEqual(im.format, "BUFR")

            # Dummy data from the stub
            self.assertEqual(im.mode, "F")
            self.assertEqual(im.size, (1, 1))

    def test_invalid_file(self):
        # Arrange
        invalid_file = "Tests/images/flower.jpg"

        # Act / Assert
        self.assertRaises(
            SyntaxError, BufrStubImagePlugin.BufrStubImageFile, invalid_file
        )

    def test_load(self):
        # Arrange
        with Image.open(TEST_FILE) as im:

            # Act / Assert: stub cannot load without an implemented handler
            self.assertRaises(IOError, im.load)

    def test_save(self):
        # Arrange
        im = hopper()
        tmpfile = self.tempfile("temp.bufr")

        # Act / Assert: stub cannot save without an implemented handler
        self.assertRaises(IOError, im.save, tmpfile)
