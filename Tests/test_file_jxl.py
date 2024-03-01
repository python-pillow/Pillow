import re
import pytest

from PIL import Image, JxlImagePlugin, features

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    skip_unless_feature,
)

try:
    from PIL import _jxl

    HAVE_JXL = True
except ImportError:
    HAVE_JXL = False

# cjxl v0.9.2 41b8cdab
# hopper.jxl: cjxl hopper.png hopper.jxl -q 75 -e 8

class TestUnsupportedJxl:
    def test_unsupported(self) -> None:
        if HAVE_JXL:
            JxlImagePlugin.SUPPORTED = False

        file_path = "Tests/images/hopper.jxl"
        with pytest.warns(UserWarning):
            with pytest.raises(OSError):
                with Image.open(file_path):
                    pass

        if HAVE_JXL:
            JxlImagePlugin.SUPPORTED = True

@skip_unless_feature("jxl")
class TestFileJxl:
    def setup_method(self) -> None:
        self.rgb_mode = "RGB"

    def test_version(self) -> None:
        _jxl.JxlDecoderVersion()
        assert re.search(r"\d+\.\d+\.\d+$", features.version_module("jxl"))

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

    def test_JxlDecode_with_invalid_args(self) -> None:
        """
        Calling decoder functions with no arguments should result in an error.
        """

        with pytest.raises(TypeError):
            _jxl.PILJxlDecoder()


