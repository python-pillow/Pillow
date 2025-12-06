from __future__ import annotations

import re

import pytest

from PIL import Image, JpegXlImagePlugin, features

from .helper import assert_image_similar_tofile, skip_unless_feature

try:
    from PIL import _jpegxl
except ImportError:
    pass

# cjxl v0.9.2 41b8cdab
# hopper.jxl: cjxl hopper.png hopper.jxl -q 75 -e 8
# 16_bit_binary.jxl: cjxl 16_bit_binary.pgm 16_bit_binary.jxl -q 100 -e 9


class TestUnsupportedJpegXl:
    def test_unsupported(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(JpegXlImagePlugin, "SUPPORTED", False)

        with pytest.raises(OSError):
            with pytest.warns(UserWarning, match="JXL support not installed"):
                with Image.open("Tests/images/hopper.jxl"):
                    pass


@skip_unless_feature("jpegxl")
class TestFileJpegXl:
    def test_version(self) -> None:
        version = features.version_module("jpegxl")
        assert version is not None
        assert re.search(r"\d+\.\d+\.\d+$", version)

    def test_read_rgb(self) -> None:
        """
        Can we read a RGB mode Jpeg XL file without error?
        Does it have the bits we expect?
        """

        with Image.open("Tests/images/hopper.jxl") as im:
            assert im.mode == "RGB"
            assert im.size == (128, 128)
            assert im.format == "JPEG XL"
            im.load()
            im.getdata()

            # generated with:
            # djxl hopper.jxl hopper_jxl_bits.ppm
            assert_image_similar_tofile(im, "Tests/images/hopper_jxl_bits.ppm", 1)

    def test_read_i16(self) -> None:
        """
        Can we read 16-bit Grayscale Jpeg XL image?
        """

        with Image.open("Tests/images/jxl/16bit_subcutaneous.cropped.jxl") as im:
            assert im.mode == "I;16"
            assert im.size == (128, 64)
            assert im.format == "JPEG XL"
            im.load()
            im.getdata()

            assert_image_similar_tofile(
                im, "Tests/images/jxl/16bit_subcutaneous.cropped.png", 1
            )

    def test_JpegXlDecode_with_invalid_args(self) -> None:
        """
        Calling decoder functions with no arguments should result in an error.
        """

        with pytest.raises(TypeError):
            _jpegxl.JpegXlDecoder()
