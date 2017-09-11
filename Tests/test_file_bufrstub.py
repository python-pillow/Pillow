from helper import unittest, PillowTestCase, hopper

from PIL import BufrStubImagePlugin, Image

TEST_FILE = "Tests/images/gfs.t06z.rassda.tm00.bufr_d"


class TestFileBufrStub(PillowTestCase):

    def test_open(self):
        # Act
        im = Image.open(TEST_FILE)

        # Assert
        self.assertEqual(im.format, "BUFR")

        # Dummy data from the stub
        self.assertEqual(im.mode, "F")
        self.assertEqual(im.size, (1, 1))

    def test_invalid_file(self):
        # Arrange
        invalid_file = "Tests/images/flower.jpg"

        # Act / Assert
        self.assertRaises(SyntaxError,
                          BufrStubImagePlugin.BufrStubImageFile, invalid_file)

    def test_load(self):
        # Arrange
        im = Image.open(TEST_FILE)

        # Act / Assert: stub cannot load without an implemented handler
        self.assertRaises(IOError, im.load)

    def test_save(self):
        # Arrange
        im = hopper()
        tmpfile = self.tempfile("temp.bufr")

        # Act / Assert: stub cannot save without an implemented handler
        self.assertRaises(IOError, im.save, tmpfile)


if __name__ == '__main__':
    unittest.main()
