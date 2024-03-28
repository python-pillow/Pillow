from __future__ import annotations

import warnings

import pytest

from PIL import Image

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    from PIL import ImageQt

from .helper import assert_image_equal, hopper

pytestmark = pytest.mark.skipif(
    not ImageQt.qt_is_installed, reason="Qt bindings are not installed"
)

ims: list[Image.Image] = []


def setup_module() -> None:
    ims.append(hopper())
    ims.append(Image.open("Tests/images/transparent.png"))
    ims.append(Image.open("Tests/images/7x13.png"))


def teardown_module() -> None:
    for im in ims:
        im.close()


def roundtrip(expected: Image.Image) -> None:
    # PIL -> Qt
    intermediate = expected.toqimage()
    # Qt -> PIL
    result = ImageQt.fromqimage(intermediate)

    if intermediate.hasAlphaChannel():
        assert_image_equal(result, expected.convert("RGBA"))
    else:
        assert_image_equal(result, expected.convert("RGB"))


def test_sanity_1() -> None:
    for im in ims:
        roundtrip(im.convert("1"))


def test_sanity_rgb() -> None:
    for im in ims:
        roundtrip(im.convert("RGB"))


def test_sanity_rgba() -> None:
    for im in ims:
        roundtrip(im.convert("RGBA"))


def test_sanity_l() -> None:
    for im in ims:
        roundtrip(im.convert("L"))


def test_sanity_p() -> None:
    for im in ims:
        roundtrip(im.convert("P"))
