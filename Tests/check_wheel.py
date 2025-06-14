from __future__ import annotations

import platform
import struct
import sys

from PIL import features

from .helper import is_pypy


def test_wheel_modules() -> None:
    expected_modules = {"pil", "tkinter", "freetype2", "littlecms2", "webp", "avif"}

    if sys.platform == "win32":
        # tkinter is not available in cibuildwheel installed CPython on Windows
        try:
            import tkinter

            assert tkinter
        except ImportError:
            expected_modules.remove("tkinter")

        # libavif is not available on Windows for x86 and ARM64 architectures
        if platform.machine() == "ARM64" or struct.calcsize("P") == 4:
            expected_modules.remove("avif")

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

    assert set(features.get_supported_features()) == expected_features
