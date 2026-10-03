from __future__ import annotations

import os
import re

import pytest

from PIL import Image, JpegXlImagePlugin, UnidentifiedImageError, features

from .helper import assert_image_similar_tofile, skip_unless_feature

try:
    from PIL import _jpegxl
except ImportError:
    pass


class TestUnsupportedJpegXl:
    def test_unsupported(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(JpegXlImagePlugin, "SUPPORTED", False)

        with pytest.raises(OSError):
            with pytest.warns(UserWarning, match="JXL support not installed"):
                Image.open("Tests/images/jxl/hopper.jxl")


@skip_unless_feature("jpegxl")
class TestFileJpegXl:
    def test_version(self) -> None:
        version = features.version_module("jpegxl")
        assert version is not None
        assert re.search(r"\d+\.\d+\.\d+$", version)

    @pytest.mark.parametrize(
        "mode, test_file",
        (
            ("1", "hopper_bw_500.png"),
            ("L", "hopper_gray.jpg"),
            ("I;16", "jxl/16bit_subcutaneous.cropped.png"),
            ("RGB", "hopper.jpg"),
            ("RGBA", "transparent.png"),
        ),
    )
    def test_read(self, mode: str, test_file: str) -> None:
        with Image.open(
            "Tests/images/jxl/"
            + os.path.splitext(os.path.basename(test_file))[0]
            + ".jxl"
        ) as im:
            assert im.format == "JPEG XL"
            assert im.mode == mode

            assert_image_similar_tofile(im, "Tests/images/" + test_file, 1.9)

    def test_unknown_mode(self) -> None:
        with pytest.raises(UnidentifiedImageError):
            Image.open("Tests/images/jxl/unknown_mode.jxl")

    def test_JpegXlDecode_with_invalid_args(self) -> None:
        """
        Calling decoder functions with no arguments should result in an error.
        """
        with pytest.raises(TypeError):
            _jpegxl.JpegXlDecoder()
