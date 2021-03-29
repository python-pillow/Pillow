import pytest

from PIL import Image

FpxImagePlugin = pytest.importorskip(
    "PIL.FpxImagePlugin", reason="olefile not installed"
)


def test_invalid_file():
    # Test an invalid OLE file
    invalid_file = "Tests/images/flower.jpg"
    with pytest.raises(SyntaxError):
        FpxImagePlugin.FpxImageFile(invalid_file)

    # Test a valid OLE file, but not an FPX file
    ole_file = "Tests/images/test-ole-file.doc"
    with pytest.raises(SyntaxError):
        FpxImagePlugin.FpxImageFile(ole_file)


def test_fpx_invalid_number_of_bands():
    with pytest.raises(OSError, match="Invalid number of bands"):
        with Image.open("Tests/images/input_bw_five_bands.fpx"):
            pass
