from helper import unittest, PillowTestCase

from PIL import Image, GbrImagePlugin


class TestFileGbr(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: GbrImagePlugin.GbrImageFile(invalid_file))

    def test_gbr_file(self):
        im = Image.open('Tests/images/gbr.gbr')

        target = Image.open('Tests/images/gbr.png')

        self.assert_image_equal(target, im)

if __name__ == '__main__':
    unittest.main()
