from PIL import Image

from helper import PillowTestCase, unittest


class TestFileBlp(PillowTestCase):
    def test_load_blp1_alpha4(self):
        im = Image.open("Tests/images/blp/blp1_alpha4.blp")
        target = Image.open("Tests/images/blp/blp1_alpha4.png")
        self.assert_image_equal(im, target)

    def test_load_blp1_alpha5(self):
        im = Image.open("Tests/images/blp/blp1_alpha5.blp")
        target = Image.open("Tests/images/blp/blp1_alpha5.png")
        self.assert_image_equal(im, target)

    def test_load_blp2_raw(self):
        im = Image.open("Tests/images/blp/blp2_raw.blp")
        target = Image.open("Tests/images/blp/blp2_raw.png")
        self.assert_image_equal(im, target)

    def test_load_blp2_dxt1(self):
        im = Image.open("Tests/images/blp/blp2_dxt1.blp")
        target = Image.open("Tests/images/blp/blp2_dxt1.png")
        self.assert_image_equal(im, target)

    def test_load_blp2_dxt1a(self):
        im = Image.open("Tests/images/blp/blp2_dxt1a.blp")
        target = Image.open("Tests/images/blp/blp2_dxt1a.png")
        self.assert_image_equal(im, target)

    def test_load_blp2_dxt3(self):
        im = Image.open("Tests/images/blp/blp2_dxt3.blp")
        target = Image.open("Tests/images/blp/blp2_dxt3.png")
        self.assert_image_equal(im, target)

    def test_load_blp2_dxt5(self):
        im = Image.open("Tests/images/blp/blp2_dxt5.blp")
        target = Image.open("Tests/images/blp/blp2_dxt5.png")
        self.assert_image_equal(im, target)


if __name__ == "__main__":
    unittest.main()
