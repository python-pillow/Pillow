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


def test_properties():
    def check(mode, *result):
        signature = (
            Image.getmodebase(mode),
            Image.getmodetype(mode),
            Image.getmodebands(mode),
            Image.getmodebandnames(mode),
        )
        assert signature == result

    check("1", "L", "L", 1, ("1",))
    check("L", "L", "L", 1, ("L",))
    check("P", "P", "L", 1, ("P",))
    check("I", "L", "I", 1, ("I",))
    check("F", "L", "F", 1, ("F",))
    check("RGB", "RGB", "L", 3, ("R", "G", "B"))
    check("RGBA", "RGB", "L", 4, ("R", "G", "B", "A"))
    check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
    check("RGBX", "RGB", "L", 4, ("R", "G", "B", "X"))
    check("CMYK", "RGB", "L", 4, ("C", "M", "Y", "K"))
    check("YCbCr", "RGB", "L", 3, ("Y", "Cb", "Cr"))
