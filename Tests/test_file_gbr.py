import pytest

from PIL import GbrImagePlugin, Image

from .helper import assert_image_equal_tofile


def test_gbr_file():
    with Image.open("Tests/images/gbr.gbr") as im:
        assert_image_equal_tofile(im, "Tests/images/gbr.png")


def test_load():
    with Image.open("Tests/images/gbr.gbr") as im:
        assert im.load()[0, 0] == (0, 0, 0, 0)

        # Test again now that it has already been loaded once
        assert im.load()[0, 0] == (0, 0, 0, 0)


def test_multiple_load_operations():
    with Image.open("Tests/images/gbr.gbr") as im:
        im.load()
        im.load()
        assert_image_equal_tofile(im, "Tests/images/gbr.png")


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        GbrImagePlugin.GbrImageFile(invalid_file)
