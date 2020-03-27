import pytest
from PIL import ImageQt

from .helper import hopper
from .test_imageqt import qpixmap_app, skip_if_qt_is_not_installed

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap

pytestmark = skip_if_qt_is_not_installed()


def test_sanity(qpixmap, tmp_path):
    for mode in ("1", "RGB", "RGBA", "L", "P"):
        data = ImageQt.toqpixmap(hopper(mode))

        assert isinstance(data, QPixmap)
        assert not data.isNull()

        # Test saving the file
        tempfile = str(tmp_path / "temp_{}.png".format(mode))
        data.save(tempfile)
