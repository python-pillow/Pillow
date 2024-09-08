from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union

import pytest

from PIL import Image, ImageQt

from .helper import assert_image_equal_tofile, assert_image_similar, hopper

if TYPE_CHECKING:
    import PyQt6
    import PySide6

    QApplication = Union[PyQt6.QtWidgets.QApplication, PySide6.QtWidgets.QApplication]
    QHBoxLayout = Union[PyQt6.QtWidgets.QHBoxLayout, PySide6.QtWidgets.QHBoxLayout]
    QImage = Union[PyQt6.QtGui.QImage, PySide6.QtGui.QImage]
    QLabel = Union[PyQt6.QtWidgets.QLabel, PySide6.QtWidgets.QLabel]
    QPainter = Union[PyQt6.QtGui.QPainter, PySide6.QtGui.QPainter]
    QPixmap = Union[PyQt6.QtGui.QPixmap, PySide6.QtGui.QPixmap]
    QPoint = Union[PyQt6.QtCore.QPoint, PySide6.QtCore.QPoint]
    QRegion = Union[PyQt6.QtGui.QRegion, PySide6.QtGui.QRegion]
    QWidget = Union[PyQt6.QtWidgets.QWidget, PySide6.QtWidgets.QWidget]

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

    class Example(QWidget):  # type: ignore[misc]
        def __init__(self) -> None:
            super().__init__()

            img = hopper().resize((1000, 1000))

            qimage = ImageQt.ImageQt(img)

            pixmap1 = getattr(ImageQt.QPixmap, "fromImage")(qimage)

            # hbox
            QHBoxLayout(self)  # type: ignore[operator]

            lbl = QLabel(self)  # type: ignore[operator]
            # Segfault in the problem
            lbl.setPixmap(pixmap1.copy())


def roundtrip(expected: Image.Image) -> None:
    result = ImageQt.fromqpixmap(ImageQt.toqpixmap(expected))
    # Qt saves all pixmaps as rgb
    assert_image_similar(result, expected.convert("RGB"), 1)


@pytest.mark.skipif(not ImageQt.qt_is_installed, reason="Qt bindings are not installed")
def test_sanity(tmp_path: Path) -> None:
    # Segfault test
    app: QApplication | None = QApplication([])  # type: ignore[operator]
    ex = Example()
    assert app  # Silence warning
    assert ex  # Silence warning

    for mode in ("1", "RGB", "RGBA", "L", "P"):
        # to QPixmap
        im = hopper(mode)
        data = ImageQt.toqpixmap(im)

        assert data.__class__.__name__ == "QPixmap"
        assert not data.isNull()

        # Test saving the file
        tempfile = str(tmp_path / f"temp_{mode}.png")
        data.save(tempfile)

        # Render the image
        imageqt = ImageQt.ImageQt(im)
        data = getattr(QPixmap, "fromImage")(imageqt)
        qt_format = getattr(QImage, "Format") if ImageQt.qt_version == "6" else QImage
        qimage = QImage(128, 128, getattr(qt_format, "Format_ARGB32"))  # type: ignore[operator]
        painter = QPainter(qimage)  # type: ignore[operator]
        image_label = QLabel()  # type: ignore[operator]
        image_label.setPixmap(data)
        image_label.render(painter, QPoint(0, 0), QRegion(0, 0, 128, 128))  # type: ignore[operator]
        painter.end()
        rendered_tempfile = str(tmp_path / f"temp_rendered_{mode}.png")
        qimage.save(rendered_tempfile)
        assert_image_equal_tofile(im.convert("RGBA"), rendered_tempfile)

        # from QPixmap
        roundtrip(hopper(mode))

    app.quit()
    app = None
