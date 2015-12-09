from helper import unittest, PillowTestCase, hopper
from test_imageqt import PillowQtTestCase

from PIL import ImageQt, Image


class TestFromQImage(PillowQtTestCase, PillowTestCase):

    files_to_test = [
        hopper(),
        Image.open('Tests/images/transparent.png'),
        Image.open('Tests/images/7x13.png'),
    ]

    def roundtrip(self, expected):
        # PIL -> Qt
        intermediate = expected.toqimage()
        # Qt -> PIL
        result = ImageQt.fromqimage(intermediate)

        if intermediate.hasAlphaChannel():
            self.assert_image_equal(result, expected.convert('RGBA'))
        else:
            self.assert_image_equal(result, expected.convert('RGB'))

    def test_sanity_1(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert('1'))

    def test_sanity_rgb(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert('RGB'))

    def test_sanity_rgba(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert('RGBA'))

    def test_sanity_l(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert('L'))

    def test_sanity_p(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert('P'))


if __name__ == '__main__':
    unittest.main()

# End of file
