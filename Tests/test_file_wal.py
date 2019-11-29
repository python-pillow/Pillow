from PIL import WalImageFile

from .helper import PillowTestCase


class TestFileWal(PillowTestCase):
    def test_open(self):
        # Arrange
        TEST_FILE = "Tests/images/hopper.wal"

        # Act
        im = WalImageFile.open(TEST_FILE)

        # Assert
        self.assertEqual(im.format, "WAL")
        self.assertEqual(im.format_description, "Quake2 Texture")
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
