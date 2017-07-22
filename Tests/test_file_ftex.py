from helper import unittest, PillowTestCase
from PIL import Image


class TestFileFtex(PillowTestCase):

    def test_load_raw(self):
        im = Image.open('Tests/images/ftex_uncompressed.ftu')
        target = Image.open('Tests/images/ftex_uncompressed.png')

        self.assert_image_equal(im, target)

    def test_load_dxt1(self):
        im = Image.open('Tests/images/ftex_dxt1.ftc')
        target = Image.open('Tests/images/ftex_dxt1.png')
        self.assert_image_similar(im, target.convert('RGBA'), 15)

if __name__ == '__main__':
    unittest.main()
