from PIL import ImageQt

from .helper import PillowTestCase, hopper
from .test_imageqt import PillowQPixmapTestCase

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap


class TestToQPixmap(PillowQPixmapTestCase, PillowTestCase):
    def test_sanity(self):
        for mode in ("1", "RGB", "RGBA", "L", "P"):
            data = ImageQt.toqpixmap(hopper(mode))

            self.assertIsInstance(data, QPixmap)
            self.assertFalse(data.isNull())

            # Test saving the file
            tempfile = self.tempfile("temp_{}.png".format(mode))
            data.save(tempfile)
