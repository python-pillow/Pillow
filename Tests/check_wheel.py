import sys

import pytest

from PIL import features


@pytest.mark.skipif(sys.platform != "win32", reason="requires Windows")
def test_windows_wheel_features():
    expected_modules = ["pil", "tkinter", "freetype2", "littlecms2", "webp"]
    expected_codecs = ["jpg", "jpg_2000", "zlib", "libtiff"]
    expected_features = [
        "webp_anim",
        "webp_mux",
        "transp_webp",
        "raqm",
        "fribidi",
        "harfbuzz",
        "libjpeg_turbo",
    ]

    assert features.get_supported_modules() == expected_modules
    assert features.get_supported_codecs() == expected_codecs
    assert features.get_supported_features() == expected_features
