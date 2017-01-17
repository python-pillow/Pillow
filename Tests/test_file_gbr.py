from PIL import Image, GbrImagePlugin
from PIL.exceptions import InvalidFileType
from helper import unittest, PillowTestCase


class TestFileGbr(PillowTestCase):

    def test_invalid_file(self):
        invalid_file = "Tests/images/no_cursors.cur"

        self.assertRaises(InvalidFileType,
                          lambda: GbrImagePlugin.GbrImageFile(invalid_file))

    def test_gbr_file(self):
        im = Image.open('Tests/images/gbr.gbr')

        target = Image.open('Tests/images/gbr.png')

        self.assert_image_equal(target, im)

if __name__ == '__main__':
    unittest.main()
