import pytest

from PIL import Image, ImageMode

from .helper import hopper


def test_sanity():
    with hopper() as im:
        im.mode

    ImageMode.getmode("1")
    ImageMode.getmode("L")
    ImageMode.getmode("P")
    ImageMode.getmode("RGB")
    ImageMode.getmode("I")
    ImageMode.getmode("F")

    m = ImageMode.getmode("1")
    assert m.mode == "1"
    assert str(m) == "1"
    assert m.bands == ("1",)
    assert m.basemode == "L"
    assert m.basetype == "L"
    assert m.typestr == "|b1"

    for mode in (
        "I;16",
        "I;16S",
        "I;16L",
        "I;16LS",
        "I;16B",
        "I;16BS",
        "I;16N",
        "I;16NS",
    ):
        m = ImageMode.getmode(mode)
        assert m.mode == mode
        assert str(m) == mode
        assert m.bands == ("I",)
        assert m.basemode == "L"
        assert m.basetype == "L"

    m = ImageMode.getmode("RGB")
    assert m.mode == "RGB"
    assert str(m) == "RGB"
    assert m.bands == ("R", "G", "B")
    assert m.basemode == "RGB"
    assert m.basetype == "L"
    assert m.typestr == "|u1"


@pytest.mark.parametrize(
    "mode, expected_base, expected_type, expected_bands, expected_band_names",
    (
        ("1", "L", "L", 1, ("1",)),
        ("L", "L", "L", 1, ("L",)),
        ("P", "P", "L", 1, ("P",)),
        ("I", "L", "I", 1, ("I",)),
        ("F", "L", "F", 1, ("F",)),
        ("RGB", "RGB", "L", 3, ("R", "G", "B")),
        ("RGBA", "RGB", "L", 4, ("R", "G", "B", "A")),
        ("RGBX", "RGB", "L", 4, ("R", "G", "B", "X")),
        ("CMYK", "RGB", "L", 4, ("C", "M", "Y", "K")),
        ("YCbCr", "RGB", "L", 3, ("Y", "Cb", "Cr")),
    ),
)
def test_properties(
    mode, expected_base, expected_type, expected_bands, expected_band_names
):
    assert Image.getmodebase(mode) == expected_base
    assert Image.getmodetype(mode) == expected_type
    assert Image.getmodebands(mode) == expected_bands
    assert Image.getmodebandnames(mode) == expected_band_names
