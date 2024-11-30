from __future__ import annotations

import warnings

import pytest

from PIL import ImageQt

from .helper import assert_image_similar, hopper

pytestmark = pytest.mark.skipif(
    not ImageQt.qt_is_installed, reason="Qt bindings are not installed"
)

if ImageQt.qt_is_installed:
    from PIL.ImageQt import qRgba


def test_rgb() -> None:
    # from https://doc.qt.io/archives/qt-4.8/qcolor.html
    # typedef QRgb
    # An ARGB quadruplet on the format #AARRGGBB,
    # equivalent to an unsigned int.
    if ImageQt.qt_version == "6":
        from PyQt6.QtGui import qRgb
    elif ImageQt.qt_version == "side6":
        from PySide6.QtGui import qRgb

    assert qRgb(0, 0, 0) == qRgba(0, 0, 0, 255)

    def checkrgb(r: int, g: int, b: int) -> None:
        val = ImageQt.rgb(r, g, b)
        val = val % 2**24  # drop the alpha
        assert val >> 16 == r
        assert ((val >> 8) % 2**8) == g
        assert val % 2**8 == b

    checkrgb(0, 0, 0)
    checkrgb(255, 0, 0)
    checkrgb(0, 255, 0)
    checkrgb(0, 0, 255)


@pytest.mark.parametrize("mode", ("1", "RGB", "RGBA", "L", "P", "I;16"))
def test_image(mode: str) -> None:
    im = hopper(mode)
    roundtripped_im = ImageQt.fromqimage(ImageQt.ImageQt(im))
    if mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")
    assert_image_similar(roundtripped_im, im, 1)


def test_closed_file() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        ImageQt.ImageQt("Tests/images/hopper.gif")
