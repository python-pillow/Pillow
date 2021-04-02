from PIL import WalImageFile


def test_open():
    # Arrange
    TEST_FILE = "Tests/images/hopper.wal"

    # Act
    im = WalImageFile.open(TEST_FILE)

    # Assert
    assert im.format == "WAL"
    assert im.format_description == "Quake2 Texture"
    assert im.mode == "P"
    assert im.size == (128, 128)
