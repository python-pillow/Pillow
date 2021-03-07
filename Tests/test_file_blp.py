from PIL import Image
import pytest

from .helper import assert_image_equal_tofile


def test_load_blp2_raw():
    with Image.open("Tests/images/blp/blp2_raw.blp") as im:
        assert_image_equal_tofile(im, "Tests/images/blp/blp2_raw.png")


def test_load_blp2_dxt1():
    with Image.open("Tests/images/blp/blp2_dxt1.blp") as im:
        assert_image_equal_tofile(im, "Tests/images/blp/blp2_dxt1.png")


def test_load_blp2_dxt1a():
    with Image.open("Tests/images/blp/blp2_dxt1a.blp") as im:
        assert_image_equal_tofile(im, "Tests/images/blp/blp2_dxt1a.png")
