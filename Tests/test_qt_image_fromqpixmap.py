from PIL import ImageQt

from .helper import PillowTestCase, hopper
from .test_imageqt import PillowQPixmapTestCase


class TestFromQPixmap(PillowQPixmapTestCase, PillowTestCase):
    def roundtrip(self, expected):
        result = ImageQt.fromqpixmap(ImageQt.toqpixmap(expected))
        # Qt saves all pixmaps as rgb
        self.assert_image_equal(result, expected.convert("RGB"))

    def test_sanity(self):
        for mode in ("1", "RGB", "RGBA", "L", "P"):
            self.roundtrip(hopper(mode))
