from PIL import Image

from .helper import PillowTestCase


class TestFileBlp(PillowTestCase):
    def test_load_blp2_raw(self):
        with Image.open("Tests/images/blp/blp2_raw.blp") as im:
            with Image.open("Tests/images/blp/blp2_raw.png") as target:
                self.assert_image_equal(im, target)

    def test_load_blp2_dxt1(self):
        with Image.open("Tests/images/blp/blp2_dxt1.blp") as im:
            with Image.open("Tests/images/blp/blp2_dxt1.png") as target:
                self.assert_image_equal(im, target)

    def test_load_blp2_dxt1a(self):
        im = Image.open("Tests/images/blp/blp2_dxt1a.blp")
        target = Image.open("Tests/images/blp/blp2_dxt1a.png")
        self.assert_image_equal(im, target)
