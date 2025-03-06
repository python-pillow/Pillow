from __future__ import annotations

import pytest

from PIL import Image

from .helper import assert_image_equal_tofile

FpxImagePlugin = pytest.importorskip(
    "PIL.FpxImagePlugin", reason="olefile not installed"
)


def test_sanity() -> None:
    with Image.open("Tests/images/input_bw_one_band.fpx") as im:
        assert im.mode == "L"
        assert im.size == (70, 46)
        assert im.format == "FPX"

        assert_image_equal_tofile(im, "Tests/images/input_bw_one_band.png")


def test_close() -> None:
    with Image.open("Tests/images/input_bw_one_band.fpx") as im:
        assert isinstance(im, FpxImagePlugin.FpxImageFile)
    assert im.ole.fp.closed

    im = Image.open("Tests/images/input_bw_one_band.fpx")
    assert isinstance(im, FpxImagePlugin.FpxImageFile)
    im.close()
    assert im.ole.fp.closed


def test_invalid_file() -> None:
    # Test an invalid OLE file
    invalid_file = "Tests/images/flower.jpg"
    with pytest.raises(SyntaxError):
        FpxImagePlugin.FpxImageFile(invalid_file)

    # Test a valid OLE file, but not an FPX file
    ole_file = "Tests/images/test-ole-file.doc"
    with pytest.raises(SyntaxError):
        FpxImagePlugin.FpxImageFile(ole_file)


def test_fpx_invalid_number_of_bands() -> None:
    with pytest.raises(OSError, match="Invalid number of bands"):
        with Image.open("Tests/images/input_bw_five_bands.fpx"):
            pass
