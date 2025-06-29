from __future__ import annotations

import platform
import sys

from PIL import features
from Tests.helper import is_pypy


def test_wheel_modules() -> None:
    expected_modules = {"pil", "tkinter", "freetype2", "littlecms2", "webp", "avif"}

    if sys.platform == "win32":
        # tkinter is not available in cibuildwheel installed CPython on Windows
        try:
            import tkinter

            assert tkinter
        except ImportError:
            expected_modules.remove("tkinter")

        # libavif is not available on Windows for ARM64 architectures
        if platform.machine() == "ARM64":
            expected_modules.remove("avif")

    elif sys.platform == "ios":
        # tkinter is not available on iOS
        # libavif is not available on iOS (for now)
        expected_modules -= {"tkinter", "avif"}

    assert set(features.get_supported_modules()) == expected_modules


def test_wheel_codecs() -> None:
    expected_codecs = {"jpg", "jpg_2000", "zlib", "libtiff"}

    assert set(features.get_supported_codecs()) == expected_codecs


def test_wheel_features() -> None:
    expected_features = {
        "webp_anim",
        "webp_mux",
        "transp_webp",
        "raqm",
        "fribidi",
        "harfbuzz",
        "libjpeg_turbo",
        "zlib_ng",
        "xcb",
    }

    if sys.platform == "win32":
        expected_features.remove("xcb")
    elif sys.platform == "darwin" and not is_pypy() and platform.processor() != "arm":
        expected_features.remove("zlib_ng")
    elif sys.platform == "ios":
        # Can't distribute raqm due to licensing, and there's no system version;
        # fribidi and harfbuzz won't be available if raqm isn't available.
        expected_features -= {"raqm", "fribidi", "harfbuzz"}

    assert set(features.get_supported_features()) == expected_features
