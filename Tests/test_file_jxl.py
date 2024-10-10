from __future__ import annotations

import re

import pytest

from PIL import Image, JpegXlImagePlugin, features

from .helper import (
    assert_image_similar_tofile,
    skip_unless_feature,
)

try:
    from PIL import _jpegxl

    HAVE_JPEGXL = True
except ImportError:
    HAVE_JPEGXL = False

# cjxl v0.9.2 41b8cdab
# hopper.jxl: cjxl hopper.png hopper.jxl -q 75 -e 8
# 16_bit_binary.jxl: cjxl 16_bit_binary.pgm 16_bit_binary.jxl -q 100 -e 9


class TestUnsupportedJpegXl:
    def test_unsupported(self) -> None:
        if HAVE_JPEGXL:
            JpegXlImagePlugin.SUPPORTED = False

        file_path = "Tests/images/hopper.jxl"
        with pytest.raises(OSError):
            with Image.open(file_path):
                pass

        if HAVE_JPEGXL:
            JpegXlImagePlugin.SUPPORTED = True


@skip_unless_feature("jpegxl")
class TestFileJpegXl:
    def setup_method(self) -> None:
        self.rgb_mode = "RGB"
        self.i16_mode = "I;16"

    def test_version(self) -> None:
        _jpegxl.JpegXlDecoderVersion()
        assert re.search(r"\d+\.\d+\.\d+$", features.version_module("jpegxl"))

    def test_read_rgb(self) -> None:
        """
        Can we read a RGB mode Jpeg XL file without error?
        Does it have the bits we expect?
        """

        with Image.open("Tests/images/hopper.jxl") as image:
            assert image.mode == self.rgb_mode
            assert image.size == (128, 128)
            assert image.format == "JPEG XL"
            image.load()
            image.getdata()

            # generated with:
            # djxl hopper.jxl hopper_jxl_bits.ppm
            assert_image_similar_tofile(image, "Tests/images/hopper_jxl_bits.ppm", 1.0)

    def test_read_i16(self) -> None:
        """
        Can we read 16-bit Grayscale Jpeg XL image?
        """

        with Image.open("Tests/images/jxl/16bit_subcutaneous.cropped.jxl") as image:
            assert image.mode == self.i16_mode
            assert image.size == (128, 64)
            assert image.format == "JPEG XL"
            image.load()
            image.getdata()

            assert_image_similar_tofile(
                image, "Tests/images/jxl/16bit_subcutaneous.cropped.png", 1.0
            )

    def test_JpegXlDecode_with_invalid_args(self) -> None:
        """
        Calling decoder functions with no arguments should result in an error.
        """

        with pytest.raises(TypeError):
            _jpegxl.PILJpegXlDecoder()
