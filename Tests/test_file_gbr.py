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


def test_multiples_operation():
    with Image.open("Tests/images/gbr.gbr") as im:
        rect = (0, 0, 10, 10)
        im.crop(rect)
        im.crop(rect)
