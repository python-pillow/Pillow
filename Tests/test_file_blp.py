from PIL import Image

from .helper import PillowTestCase, assert_image_equal


class TestFileBlp(PillowTestCase):
    def test_load_blp2_raw(self):
        with Image.open("Tests/images/blp/blp2_raw.blp") as im:
            with Image.open("Tests/images/blp/blp2_raw.png") as target:
                assert_image_equal(im, target)

    def test_load_blp2_dxt1(self):
        with Image.open("Tests/images/blp/blp2_dxt1.blp") as im:
            with Image.open("Tests/images/blp/blp2_dxt1.png") as target:
                assert_image_equal(im, target)

    def test_load_blp2_dxt1a(self):
        with Image.open("Tests/images/blp/blp2_dxt1a.blp") as im:
            with Image.open("Tests/images/blp/blp2_dxt1a.png") as target:
                assert_image_equal(im, target)
