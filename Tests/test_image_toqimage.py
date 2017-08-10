from helper import unittest, PillowTestCase, hopper
from test_imageqt import PillowQtTestCase

from PIL import ImageQt, Image


if ImageQt.qt_is_installed:
    from PIL.ImageQt import QImage

    try:
        from PyQt5 import QtGui
        from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication
        QT_VERSION = 5
    except (ImportError, RuntimeError):
        try:
            from PyQt4 import QtGui
            from PyQt4.QtGui import QWidget, QHBoxLayout, QLabel, QApplication
            QT_VERSION = 4
        except (ImportError, RuntimeError):
            from PySide import QtGui
            from PySide.QtGui import QWidget, QHBoxLayout, QLabel, QApplication
            QT_VERSION = 4


class TestToQImage(PillowQtTestCase, PillowTestCase):

    def test_sanity(self):
        PillowQtTestCase.setUp(self)
        for mode in ('RGB', 'RGBA', 'L', 'P', '1'):
            src = hopper(mode)
            data = ImageQt.toqimage(src)

            self.assertIsInstance(data, QImage)
            self.assertFalse(data.isNull())

            # reload directly from the qimage
            rt = ImageQt.fromqimage(data)
            if mode in ('L', 'P', '1'):
                self.assert_image_equal(rt, src.convert('RGB'))
            else:
                self.assert_image_equal(rt, src)

            if mode == '1':
                # BW appears to not save correctly on QT4 and QT5
                # kicks out errors on console:
                # libpng warning: Invalid color type/bit depth combination in IHDR
                # libpng error: Invalid IHDR data
                continue

            # Test saving the file
            tempfile = self.tempfile('temp_{}.png'.format(mode))
            data.save(tempfile)

            # Check that it actually worked.
            reloaded = Image.open(tempfile)
            # Gray images appear to come back in palette mode.
            # They're roughly equivalent
            if QT_VERSION == 4 and mode == 'L':
                src = src.convert('P')
            self.assert_image_equal(reloaded, src)

    def test_segfault(self):
        PillowQtTestCase.setUp(self)

        app = QApplication([])
        ex = Example()
        assert(app)  # Silence warning
        assert(ex)   # Silence warning


if ImageQt.qt_is_installed:
    class Example(QWidget):

        def __init__(self):
            super(Example, self).__init__()

            img = hopper().resize((1000, 1000))

            qimage = ImageQt.ImageQt(img)

            pixmap1 = QtGui.QPixmap.fromImage(qimage)

            hbox = QHBoxLayout(self)

            lbl = QLabel(self)
            # Segfault in the problem
            lbl.setPixmap(pixmap1.copy())


if __name__ == '__main__':
    unittest.main()
