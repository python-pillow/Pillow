import pytest
from PIL import ImageQt

from .helper import PillowTestCase, hopper

if ImageQt.qt_is_installed:
    from PIL.ImageQt import qRgba

    def skip_if_qt_is_not_installed():
        pass


else:

    def skip_if_qt_is_not_installed():
        return pytest.mark.skip(reason="Qt bindings are not installed")


class PillowQtTestCase:
    def setUp(self):
        skip_if_qt_is_not_installed(self)

    def tearDown(self):
        pass


class PillowQPixmapTestCase(PillowQtTestCase):
    def setUp(self):
        super().setUp()
        try:
            if ImageQt.qt_version == "5":
                from PyQt5.QtGui import QGuiApplication
            elif ImageQt.qt_version == "side2":
                from PySide2.QtGui import QGuiApplication
        except ImportError:
            self.skipTest("QGuiApplication not installed")

        self.app = QGuiApplication([])

    def tearDown(self):
        super().tearDown()
        self.app.quit()


class TestImageQt(PillowQtTestCase, PillowTestCase):
    def test_rgb(self):
        # from https://doc.qt.io/archives/qt-4.8/qcolor.html
        # typedef QRgb
        # An ARGB quadruplet on the format #AARRGGBB,
        # equivalent to an unsigned int.
        if ImageQt.qt_version == "5":
            from PyQt5.QtGui import qRgb
        elif ImageQt.qt_version == "side2":
            from PySide2.QtGui import qRgb

        assert qRgb(0, 0, 0) == qRgba(0, 0, 0, 255)

        def checkrgb(r, g, b):
            val = ImageQt.rgb(r, g, b)
            val = val % 2 ** 24  # drop the alpha
            assert val >> 16 == r
            assert ((val >> 8) % 2 ** 8) == g
            assert val % 2 ** 8 == b

        checkrgb(0, 0, 0)
        checkrgb(255, 0, 0)
        checkrgb(0, 255, 0)
        checkrgb(0, 0, 255)

    def test_image(self):
        for mode in ("1", "RGB", "RGBA", "L", "P"):
            ImageQt.ImageQt(hopper(mode))
