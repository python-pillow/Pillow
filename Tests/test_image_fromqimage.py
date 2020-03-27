import pytest
from PIL import Image, ImageQt

from .helper import PillowTestCase, assert_image_equal, hopper
from .test_imageqt import skip_if_qt_is_not_installed


pytestmark = skip_if_qt_is_not_installed()

@pytest.fixture
def test_images():
    ims = [
        hopper(),
        Image.open("Tests/images/transparent.png"),
        Image.open("Tests/images/7x13.png"),
    ]
    try:
        yield ims
    finally:
        for im in ims.values():
            im.close()

def roundtrip(expected):
    # PIL -> Qt
    intermediate = expected.toqimage()
    # Qt -> PIL
    result = ImageQt.fromqimage(intermediate)

    if intermediate.hasAlphaChannel():
        assert_image_equal(result, expected.convert("RGBA"))
    else:
        assert_image_equal(result, expected.convert("RGB"))

def test_sanity_1(test_images):
    for im in test_images:
        roundtrip(im.convert("1"))

def test_sanity_rgb(test_images):
    for im in test_images:
        roundtrip(im.convert("RGB"))

def test_sanity_rgba(test_images):
    for im in test_images:
        roundtrip(im.convert("RGBA"))

def test_sanity_l(test_images):
    for im in test_images:
        roundtrip(im.convert("L"))

def test_sanity_p(test_images):
    for im in test_images:
        roundtrip(im.convert("P"))
