import pytest

from PIL import Image, PixarImagePlugin

from .helper import assert_image_similar, hopper

TEST_FILE = "Tests/images/hopper.pxr"


def test_sanity():
    with Image.open(TEST_FILE) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "PIXAR"
        assert im.get_format_mimetype() is None

        im2 = hopper()
        assert_image_similar(im, im2, 4.8)


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        PixarImagePlugin.PixarImageFile(invalid_file)
