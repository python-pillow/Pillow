from PIL import WalImageFile

from .helper import assert_image_equal_tofile


def test_open():
    # Arrange
    TEST_FILE = "Tests/images/hopper.wal"

    # Act
    with WalImageFile.open(TEST_FILE) as im:

        # Assert
        assert im.format == "WAL"
        assert im.format_description == "Quake2 Texture"
        assert im.mode == "P"
        assert im.size == (128, 128)

        assert isinstance(im, WalImageFile.WalImageFile)

        assert_image_equal_tofile(im, "Tests/images/hopper_wal.png")
