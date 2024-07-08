from __future__ import annotations

import sys

from PIL import features


def test_wheel_modules() -> None:
    expected_modules = {"pil", "tkinter", "freetype2", "littlecms2", "webp"}

    # tkinter is not available in cibuildwheel installed CPython on Windows
    try:
        import tkinter

        assert tkinter
    except ImportError:
        expected_modules.remove("tkinter")

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
        "xcb",
    }

    if sys.platform == "win32":
        expected_features.remove("xcb")

    assert set(features.get_supported_features()) == expected_features
