from helper import unittest, PillowTestCase, hopper
from test_imageqt import PillowQtTestCase

from PIL import ImageQt


if ImageQt.qt_is_installed:
    from PIL.ImageQt import QImage, QPixmap

    try:
        from PyQt5 import QtGui
    except (ImportError, RuntimeError):
        try:
            from PyQt4 import QtGui
        except (ImportError, RuntimeError):
            from PySide import QtGui
            



class TestToQImage(PillowQtTestCase, PillowTestCase):

    def test_sanity(self):
        PillowQtTestCase.setUp(self)
        for mode in ('1', 'RGB', 'RGBA', 'L', 'P'):
            data = ImageQt.toqimage(hopper(mode))

            self.assertIsInstance(data, QImage)
            self.assertFalse(data.isNull())

            # Test saving the file
            tempfile = self.tempfile('temp_{}.png'.format(mode))
            data.save(tempfile)


    def test_segfault(self):
        PillowQtTestCase.setUp(self)

        app = QtGui.QApplication([])
        ex = Example()


if ImageQt.qt_is_installed:
    class Example(QtGui.QWidget):

        def __init__(self):
            super(Example, self).__init__()

            img = hopper().resize((1000,1000))

            qimage = ImageQt.ImageQt(img)

            pixmap1 = QtGui.QPixmap.fromImage(qimage)

            hbox = QtGui.QHBoxLayout(self)

            lbl = QtGui.QLabel(self)
            # Segfault in the problem
            lbl.setPixmap(pixmap1.copy())




def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())




if __name__ == '__main__':
    unittest.main()
