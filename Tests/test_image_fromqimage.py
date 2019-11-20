from PIL import Image, ImageQt

from .helper import PillowTestCase, hopper
from .test_imageqt import PillowQtTestCase


class TestFromQImage(PillowQtTestCase, PillowTestCase):
    def setUp(self):
        super().setUp()
        self.files_to_test = [
            hopper(),
            Image.open("Tests/images/transparent.png"),
            Image.open("Tests/images/7x13.png"),
        ]
        for im in self.files_to_test:
            self.addCleanup(im.close)

    def roundtrip(self, expected):
        # PIL -> Qt
        intermediate = expected.toqimage()
        # Qt -> PIL
        result = ImageQt.fromqimage(intermediate)

        if intermediate.hasAlphaChannel():
            self.assert_image_equal(result, expected.convert("RGBA"))
        else:
            self.assert_image_equal(result, expected.convert("RGB"))

    def test_sanity_1(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert("1"))

    def test_sanity_rgb(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert("RGB"))

    def test_sanity_rgba(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert("RGBA"))

    def test_sanity_l(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert("L"))

    def test_sanity_p(self):
        for im in self.files_to_test:
            self.roundtrip(im.convert("P"))
