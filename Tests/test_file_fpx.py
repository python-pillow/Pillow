import pytest

from PIL import Image

from .helper import assert_image_equal, assert_image_equal_tofile

FpxImagePlugin = pytest.importorskip(
    "PIL.FpxImagePlugin", reason="olefile not installed"
)


def test_sanity():
    with Image.open("Tests/images/input_bw_one_band.fpx") as im:
        assert im.mode == "L"
        assert im.size == (70, 46)
        assert im.format == "FPX"

        assert_image_equal_tofile(im, "Tests/images/input_bw_one_band.png")


def test_fill():
    with Image.open("Tests/images/input_bw_fill.fpx") as im:
        # The first tile has been hexedited to fill with white
        compression, (x, y, x1, y1) = im.tile[0][:2]
        assert compression == "fpx_fill"
        assert (x, y, x1, y1) == (0, 0, 64, 46)

        with Image.open("Tests/images/input_bw_one_band.png") as im2:
            for x in range(x1):
                for y in range(y1):
                    im2.putpixel((x, y), 255)
            assert_image_equal(im, im2)


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
