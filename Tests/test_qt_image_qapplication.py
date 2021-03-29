import pytest

from PIL import ImageQt

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

if ImageQt.qt_is_installed:
    from PIL.ImageQt import QPixmap

    if ImageQt.qt_version == "6":
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QImage, QPainter, QRegion
        from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget
    elif ImageQt.qt_version == "side6":
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QImage, QPainter, QRegion
        from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget
    elif ImageQt.qt_version == "5":
        from PyQt5.QtCore import QPoint
        from PyQt5.QtGui import QImage, QPainter, QRegion
        from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget
    elif ImageQt.qt_version == "side2":
        from PySide2.QtCore import QPoint
        from PySide2.QtGui import QImage, QPainter, QRegion
        from PySide2.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

    class Example(QWidget):
        def __init__(self):
            super().__init__()

            img = hopper().resize((1000, 1000))

            qimage = ImageQt.ImageQt(img)

            pixmap1 = ImageQt.QPixmap.fromImage(qimage)

            QHBoxLayout(self)  # hbox

            lbl = QLabel(self)
            # Segfault in the problem
            lbl.setPixmap(pixmap1.copy())


def roundtrip(expected):
    result = ImageQt.fromqpixmap(ImageQt.toqpixmap(expected))
    # Qt saves all pixmaps as rgb
    assert_image_equal(result, expected.convert("RGB"))


@pytest.mark.skipif(not ImageQt.qt_is_installed, reason="Qt bindings are not installed")
def test_sanity(tmp_path):
    # Segfault test
    app = QApplication([])
    ex = Example()
    assert app  # Silence warning
    assert ex  # Silence warning

    for mode in ("1", "RGB", "RGBA", "L", "P"):
        # to QPixmap
        im = hopper(mode)
        data = ImageQt.toqpixmap(im)

        assert isinstance(data, QPixmap)
        assert not data.isNull()

        # Test saving the file
        tempfile = str(tmp_path / f"temp_{mode}.png")
        data.save(tempfile)

        # Render the image
        qimage = ImageQt.ImageQt(im)
        data = QPixmap.fromImage(qimage)
        qt_format = QImage.Format if ImageQt.qt_version == "6" else QImage
        qimage = QImage(128, 128, qt_format.Format_ARGB32)
        painter = QPainter(qimage)
        image_label = QLabel()
        image_label.setPixmap(data)
        image_label.render(painter, QPoint(0, 0), QRegion(0, 0, 128, 128))
        painter.end()
        rendered_tempfile = str(tmp_path / f"temp_rendered_{mode}.png")
        qimage.save(rendered_tempfile)
        assert_image_equal_tofile(im.convert("RGBA"), rendered_tempfile)

        # from QPixmap
        roundtrip(hopper(mode))

    app.quit()
    app = None
