import pytest

from PIL import ImageQt

from .helper import hopper

pytestmark = pytest.mark.skipif(
    not ImageQt.qt_is_installed, reason="Qt bindings are not installed"
)

if ImageQt.qt_is_installed:
    from PIL.ImageQt import qRgba


def test_rgb():
    # from https://doc.qt.io/archives/qt-4.8/qcolor.html
    # typedef QRgb
    # An ARGB quadruplet on the format #AARRGGBB,
    # equivalent to an unsigned int.
    if ImageQt.qt_version == "6":
        from PyQt6.QtGui import qRgb
    elif ImageQt.qt_version == "side6":
        from PySide6.QtGui import qRgb
    elif ImageQt.qt_version == "5":
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


def test_image():
    for mode in ("1", "RGB", "RGBA", "L", "P"):
        ImageQt.ImageQt(hopper(mode))


def test_closed_file():
    with pytest.warns(None) as record:
        ImageQt.ImageQt("Tests/images/hopper.gif")

    assert not record
