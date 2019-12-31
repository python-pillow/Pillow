from PIL import FitsStubImagePlugin, Image

from .helper import PillowTestCase

TEST_FILE = "Tests/images/hopper.fits"


class TestFileFitsStub(PillowTestCase):
    def test_open(self):
        # Act
        with Image.open(TEST_FILE) as im:

            # Assert
            self.assertEqual(im.format, "FITS")

            # Dummy data from the stub
            self.assertEqual(im.mode, "F")
            self.assertEqual(im.size, (1, 1))

    def test_invalid_file(self):
        # Arrange
        invalid_file = "Tests/images/flower.jpg"

        # Act / Assert
        self.assertRaises(
            SyntaxError, FitsStubImagePlugin.FITSStubImageFile, invalid_file
        )

    def test_load(self):
        # Arrange
        with Image.open(TEST_FILE) as im:

            # Act / Assert: stub cannot load without an implemented handler
            self.assertRaises(IOError, im.load)

    def test_save(self):
        # Arrange
        with Image.open(TEST_FILE) as im:
            dummy_fp = None
            dummy_filename = "dummy.filename"

            # Act / Assert: stub cannot save without an implemented handler
            self.assertRaises(IOError, im.save, dummy_filename)
            self.assertRaises(
                IOError, FitsStubImagePlugin._save, im, dummy_fp, dummy_filename
            )
