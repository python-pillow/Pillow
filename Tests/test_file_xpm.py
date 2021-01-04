import pytest

from PIL import Image, XpmImagePlugin

from .helper import assert_image_similar, hopper

TEST_FILE = "Tests/images/hopper.xpm"


def test_sanity():
    with Image.open(TEST_FILE) as im:
        im.load()
        assert im.mode == "P"
        assert im.size == (128, 128)
        assert im.format == "XPM"

        # large error due to quantization->44 colors.
        assert_image_similar(im.convert("RGB"), hopper("RGB"), 60)


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        XpmImagePlugin.XpmImageFile(invalid_file)


def test_load_read():
    # Arrange
    with Image.open(TEST_FILE) as im:
        dummy_bytes = 1

        # Act
        data = im.load_read(dummy_bytes)

    # Assert
    assert len(data) == 16384
