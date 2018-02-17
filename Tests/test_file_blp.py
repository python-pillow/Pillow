from PIL import Image

from helper import PillowTestCase, unittest


class TestFileBlp(PillowTestCase):
    def test_load_blp2_dxt1(self):
        im = Image.open("Tests/images/blp2_dxt1.blp")
        target = Image.open("Tests/images/blp2_dxt1.png")
        self.assert_image_similar(im, target.convert("RGBA"), 15)


if __name__ == "__main__":
    unittest.main()
