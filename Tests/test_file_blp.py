from PIL import Image

from .helper import assert_image_equal


def test_load_blp2_raw():
    with Image.open("Tests/images/blp/blp2_raw.blp") as im:
        with Image.open("Tests/images/blp/blp2_raw.png") as target:
            assert_image_equal(im, target)


def test_load_blp2_dxt1():
    with Image.open("Tests/images/blp/blp2_dxt1.blp") as im:
        with Image.open("Tests/images/blp/blp2_dxt1.png") as target:
            assert_image_equal(im, target)


def test_load_blp2_dxt1a():
    with Image.open("Tests/images/blp/blp2_dxt1a.blp") as im:
        with Image.open("Tests/images/blp/blp2_dxt1a.png") as target:
            assert_image_equal(im, target)
