from .helper import PillowTestCase, hopper, unittest

from PIL import ImageQt


if ImageQt.qt_is_installed:
    from PIL.ImageQt import qRgba


class PillowQtTestCase(object):
    @classmethod
    def setUpClass(cls):
        if not ImageQt.qt_is_installed:
            raise unittest.SkipTest('Qt bindings are not installed')

    def tearDown(self):
        pass


class PillowQPixmapTestCase(PillowQtTestCase):
    @classmethod
    def setUpClass(cls):
        super(PillowQPixmapTestCase, cls).setUpClass()

        try:
            if ImageQt.qt_version == '5':
                from PyQt5.QtGui import QGuiApplication
            elif ImageQt.qt_version == '4':
                from PyQt4.QtGui import QGuiApplication
            elif ImageQt.qt_version == 'side':
                from PySide.QtGui import QGuiApplication
            elif ImageQt.qt_version == 'side2':
                from PySide2.QtGui import QGuiApplication
        except ImportError:
            raise unittest.SkipTest('QGuiApplication not installed')

        cls.app = QGuiApplication([])

    def tearDown(self):
        PillowQtTestCase.tearDown(self)
        self.app.quit()


class TestImageQt(PillowQtTestCase, PillowTestCase):

    def test_rgb(self):
        # from https://doc.qt.io/archives/qt-4.8/qcolor.html
        # typedef QRgb
        # An ARGB quadruplet on the format #AARRGGBB,
        # equivalent to an unsigned int.
        if ImageQt.qt_version == '5':
            from PyQt5.QtGui import qRgb
        elif ImageQt.qt_version == '4':
            from PyQt4.QtGui import qRgb
        elif ImageQt.qt_version == 'side':
            from PySide.QtGui import qRgb
        elif ImageQt.qt_version == 'side2':
            from PySide2.QtGui import qRgb

        self.assertEqual(qRgb(0, 0, 0), qRgba(0, 0, 0, 255))

        def checkrgb(r, g, b):
            val = ImageQt.rgb(r, g, b)
            val = val % 2**24  # drop the alpha
            self.assertEqual(val >> 16, r)
            self.assertEqual(((val >> 8) % 2**8), g)
            self.assertEqual(val % 2**8, b)

        checkrgb(0, 0, 0)
        checkrgb(255, 0, 0)
        checkrgb(0, 255, 0)
        checkrgb(0, 0, 255)

    def test_image(self):
        for mode in ('1', 'RGB', 'RGBA', 'L', 'P'):
            ImageQt.ImageQt(hopper(mode))
