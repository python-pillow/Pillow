import pytest
from PIL import Image, ImageQt

from .helper import assert_image_equal, hopper

pytestmark = pytest.mark.skipif(
    not ImageQt.qt_is_installed, reason="Qt bindings are not installed"
)

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QImage

    try:
        from PyQt5 import QtGui
        from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication
    except (ImportError, RuntimeError):
        from PySide2 import QtGui
        from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication


def test_sanity(tmp_path):
    for mode in ("RGB", "RGBA", "L", "P", "1"):
        src = hopper(mode)
        data = ImageQt.toqimage(src)

        assert isinstance(data, QImage)
        assert not data.isNull()

        # reload directly from the qimage
        rt = ImageQt.fromqimage(data)
        if mode in ("L", "P", "1"):
            assert_image_equal(rt, src.convert("RGB"))
        else:
            assert_image_equal(rt, src)

        if mode == "1":
            # BW appears to not save correctly on QT4 and QT5
            # kicks out errors on console:
            #     libpng warning: Invalid color type/bit depth combination
            #                     in IHDR
            #     libpng error: Invalid IHDR data
            continue

        # Test saving the file
        tempfile = str(tmp_path / "temp_{}.png".format(mode))
        data.save(tempfile)

        # Check that it actually worked.
        with Image.open(tempfile) as reloaded:
            assert_image_equal(reloaded, src)


def test_segfault():
    app = QApplication([])
    ex = Example()
    assert app  # Silence warning
    assert ex  # Silence warning


if ImageQt.qt_is_installed:

    class Example(QWidget):
        def __init__(self):
            super().__init__()

            img = hopper().resize((1000, 1000))

            qimage = ImageQt.ImageQt(img)

            pixmap1 = QtGui.QPixmap.fromImage(qimage)

            QHBoxLayout(self)  # hbox

            lbl = QLabel(self)
            # Segfault in the problem
            lbl.setPixmap(pixmap1.copy())
