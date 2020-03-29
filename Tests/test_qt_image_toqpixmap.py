from PIL import ImageQt

from .helper import hopper
from .test_imageqt import PillowQPixmapTestCase

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap


class TestToQPixmap(PillowQPixmapTestCase):
    def test_sanity(self, tmp_path):
        for mode in ("1", "RGB", "RGBA", "L", "P"):
            data = ImageQt.toqpixmap(hopper(mode))

            assert isinstance(data, QPixmap)
            assert not data.isNull()

            # Test saving the file
            tempfile = str(tmp_path / "temp_{}.png".format(mode))
            data.save(tempfile)
