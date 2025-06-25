from __future__ import annotations

import io
import re
from typing import Callable

import pytest

from PIL import features

from .helper import skip_unless_feature


def test_check() -> None:
    # Check the correctness of the convenience function
    for module in features.modules:
        assert features.check_module(module) == features.check(module)
    for codec in features.codecs:
        assert features.check_codec(codec) == features.check(codec)
    for feature in features.features:
        if "webp" in feature:
            with pytest.warns(DeprecationWarning, match="webp"):
                assert features.check_feature(feature) == features.check(feature)
        else:
            assert features.check_feature(feature) == features.check(feature)


def test_version() -> None:
    # Check the correctness of the convenience function
    # and the format of version numbers

    def test(name: str, function: Callable[[str], str | None]) -> None:
        version = features.version(name)
        if not features.check(name):
            assert version is None
        else:
            assert function(name) == version
            if name != "PIL":
                if version is not None:
                    if name == "zlib" and features.check_feature("zlib_ng"):
                        version = re.sub(".zlib-ng$", "", version)
                    elif name == "libtiff":
                        version = re.sub("t$", "", version)
                assert version is None or re.search(r"\d+(\.\d+)*$", version)

    for module in features.modules:
        test(module, features.version_module)
    for codec in features.codecs:
        test(codec, features.version_codec)
    for feature in features.features:
        if "webp" in feature:
            with pytest.warns(DeprecationWarning, match="webp"):
                test(feature, features.version_feature)
        else:
            test(feature, features.version_feature)


def test_webp_transparency() -> None:
    with pytest.warns(DeprecationWarning, match="transp_webp"):
        assert (features.check("transp_webp") or False) == features.check_module("webp")


def test_webp_mux() -> None:
    with pytest.warns(DeprecationWarning, match="webp_mux"):
        assert (features.check("webp_mux") or False) == features.check_module("webp")


def test_webp_anim() -> None:
    with pytest.warns(DeprecationWarning, match="webp_anim"):
        assert (features.check("webp_anim") or False) == features.check_module("webp")


@skip_unless_feature("libjpeg_turbo")
def test_libjpeg_turbo_version() -> None:
    version = features.version("libjpeg_turbo")
    assert version is not None
    assert re.search(r"\d+\.\d+\.\d+$", version)


@skip_unless_feature("libimagequant")
def test_libimagequant_version() -> None:
    version = features.version("libimagequant")
    assert version is not None
    assert re.search(r"\d+\.\d+\.\d+$", version)


@pytest.mark.parametrize("feature", features.modules)
def test_check_modules(feature: str) -> None:
    assert features.check_module(feature) in [True, False]


@pytest.mark.parametrize("feature", features.codecs)
def test_check_codecs(feature: str) -> None:
    assert features.check_codec(feature) in [True, False]


def test_check_warns_on_nonexistent() -> None:
    with pytest.warns(UserWarning, match="Unknown feature 'typo'."):
        has_feature = features.check("typo")
    assert has_feature is False


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
def test_pilinfo(supported_formats: bool) -> None:
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
