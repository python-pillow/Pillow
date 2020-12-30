import pytest

from PIL import GbrImagePlugin, Image

from .helper import assert_image_equal


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        GbrImagePlugin.GbrImageFile(invalid_file)


def test_gbr_file():
    with Image.open("Tests/images/gbr.gbr") as im:
        with Image.open("Tests/images/gbr.png") as target:
            assert_image_equal(target, im)


def test_multiple_load_operations():
    with Image.open("Tests/images/gbr.gbr") as im:
        im.load()
        im.load()
        with Image.open("Tests/images/gbr.png") as target:
            assert_image_equal(target, im)
