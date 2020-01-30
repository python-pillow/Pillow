from PIL import Image

from .helper import PillowTestCase, assert_image_equal, assert_image_similar


class TestFileFtex(PillowTestCase):
    def test_load_raw(self):
        with Image.open("Tests/images/ftex_uncompressed.ftu") as im:
            with Image.open("Tests/images/ftex_uncompressed.png") as target:
                assert_image_equal(im, target)

    def test_load_dxt1(self):
        with Image.open("Tests/images/ftex_dxt1.ftc") as im:
            with Image.open("Tests/images/ftex_dxt1.png") as target:
                assert_image_similar(im, target.convert("RGBA"), 15)
