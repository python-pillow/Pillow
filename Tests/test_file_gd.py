from PIL import GdImageFile, UnidentifiedImageError

from .helper import PillowTestCase

TEST_GD_FILE = "Tests/images/hopper.gd"


class TestFileGd(PillowTestCase):
    def test_sanity(self):
        with GdImageFile.open(TEST_GD_FILE) as im:
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.format, "GD")

    def test_bad_mode(self):
        self.assertRaises(ValueError, GdImageFile.open, TEST_GD_FILE, "bad mode")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(UnidentifiedImageError, GdImageFile.open, invalid_file)
