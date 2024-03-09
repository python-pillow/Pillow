from __future__ import annotations

import io
import re
from typing import Callable

import pytest

from PIL import features

from .helper import skip_unless_feature

try:
    from PIL import _webp
except ImportError:
    pass


def test_check() -> None:
    # Check the correctness of the convenience function
    for module in features.modules:
        assert features.check_module(module) == features.check(module)
    for codec in features.codecs:
        assert features.check_codec(codec) == features.check(codec)
    for feature in features.features:
        assert features.check_feature(feature) == features.check(feature)


def test_version() -> None:
    # Check the correctness of the convenience function
    # and the format of version numbers

    def test(name: str, function: Callable[[str], bool]) -> None:
        version = features.version(name)
        if not features.check(name):
            assert version is None
        else:
            assert function(name) == version
            if name != "PIL":
                assert version is None or re.search(r"\d+(\.\d+)*$", version)

    for module in features.modules:
        test(module, features.version_module)
    for codec in features.codecs:
        test(codec, features.version_codec)
    for feature in features.features:
        test(feature, features.version_feature)


@skip_unless_feature("webp")
def test_webp_transparency() -> None:
    assert features.check("transp_webp") != _webp.WebPDecoderBuggyAlpha()
    assert features.check("transp_webp") == _webp.HAVE_TRANSPARENCY


@skip_unless_feature("webp")
def test_webp_mux() -> None:
    assert features.check("webp_mux") == _webp.HAVE_WEBPMUX


@skip_unless_feature("webp")
def test_webp_anim() -> None:
    assert features.check("webp_anim") == _webp.HAVE_WEBPANIM


@skip_unless_feature("libjpeg_turbo")
def test_libjpeg_turbo_version() -> None:
    assert re.search(r"\d+\.\d+\.\d+$", features.version("libjpeg_turbo"))


@skip_unless_feature("libimagequant")
def test_libimagequant_version() -> None:
    assert re.search(r"\d+\.\d+\.\d+$", features.version("libimagequant"))


@pytest.mark.parametrize("feature", features.modules)
def test_check_modules(feature: str) -> None:
    assert features.check_module(feature) in [True, False]


@pytest.mark.parametrize("feature", features.codecs)
def test_check_codecs(feature: str) -> None:
    assert features.check_codec(feature) in [True, False]


def test_check_warns_on_nonexistent() -> None:
    with pytest.warns(UserWarning) as cm:
        has_feature = features.check("typo")
    assert has_feature is False
    assert str(cm[-1].message) == "Unknown feature 'typo'."


def test_supported_modules() -> None:
    assert isinstance(features.get_supported_modules(), list)
    assert isinstance(features.get_supported_codecs(), list)
    assert isinstance(features.get_supported_features(), list)
    assert isinstance(features.get_supported(), list)


def test_unsupported_codec() -> None:
    # Arrange
    codec = "unsupported_codec"
    # Act / Assert
    with pytest.raises(ValueError):
        features.check_codec(codec)
    with pytest.raises(ValueError):
        features.version_codec(codec)


def test_unsupported_module() -> None:
    # Arrange
    module = "unsupported_module"
    # Act / Assert
    with pytest.raises(ValueError):
        features.check_module(module)
    with pytest.raises(ValueError):
        features.version_module(module)


@pytest.mark.parametrize("supported_formats", (True, False))
def test_pilinfo(supported_formats) -> None:
    buf = io.StringIO()
    features.pilinfo(buf, supported_formats=supported_formats)
    out = buf.getvalue()
    lines = out.splitlines()
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Pillow ")
    assert lines[2].startswith("Python ")
    lines = lines[3:]
    while lines[0].startswith("    "):
        lines = lines[1:]
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Python executable is")
    lines = lines[2:]
    if lines[0].startswith("Environment Python files loaded from"):
        lines = lines[1:]
    assert lines[0].startswith("System Python files loaded from")
    assert lines[1] == "-" * 68
    assert lines[2].startswith("Python Pillow modules loaded from ")
    assert lines[3].startswith("Binary Pillow modules loaded from ")
    assert lines[4] == "-" * 68
    jpeg = (
        "\n"
        + "-" * 68
        + "\n"
        + "JPEG image/jpeg\n"
        + "Extensions: .jfif, .jpe, .jpeg, .jpg\n"
        + "Features: open, save\n"
        + "-" * 68
        + "\n"
    )
    assert supported_formats == (jpeg in out)
