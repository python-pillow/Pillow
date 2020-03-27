import pytest
from PIL import ImageQt

from .helper import assert_image_equal, hopper
from .test_imageqt import qpixmap_app, skip_if_qt_is_not_installed

pytestmark = skip_if_qt_is_not_installed()


def roundtrip(expected):
    result = ImageQt.fromqpixmap(ImageQt.toqpixmap(expected))
    # Qt saves all pixmaps as rgb
    assert_image_equal(result, expected.convert("RGB"))


def test_sanity(qpixmap_app):
    for mode in ("1", "RGB", "RGBA", "L", "P"):
        roundtrip(hopper(mode))
