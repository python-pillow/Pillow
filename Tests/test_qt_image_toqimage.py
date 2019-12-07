from PIL import Image, ImageQt

from .helper import PillowTestCase, hopper
from .test_imageqt import PillowQtTestCase

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QImage

    try:
        from PyQt5 import QtGui
        from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication
    except (ImportError, RuntimeError):
        from PySide2 import QtGui
        from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication


class TestToQImage(PillowQtTestCase, PillowTestCase):
    def test_sanity(self):
        for mode in ("RGB", "RGBA", "L", "P", "1"):
            src = hopper(mode)
            data = ImageQt.toqimage(src)

            self.assertIsInstance(data, QImage)
            self.assertFalse(data.isNull())

            # reload directly from the qimage
            rt = ImageQt.fromqimage(data)
            if mode in ("L", "P", "1"):
                self.assert_image_equal(rt, src.convert("RGB"))
            else:
                self.assert_image_equal(rt, src)

            if mode == "1":
                # BW appears to not save correctly on QT4 and QT5
                # kicks out errors on console:
                #     libpng warning: Invalid color type/bit depth combination
                #                     in IHDR
                #     libpng error: Invalid IHDR data
                continue

            # Test saving the file
            tempfile = self.tempfile("temp_{}.png".format(mode))
            data.save(tempfile)

            # Check that it actually worked.
            with Image.open(tempfile) as reloaded:
                self.assert_image_equal(reloaded, src)

    def test_segfault(self):
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
