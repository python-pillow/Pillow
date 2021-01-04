from PIL import Image


def test_getbands():
    assert Image.new("1", (1, 1)).getbands() == ("1",)
    assert Image.new("L", (1, 1)).getbands() == ("L",)
    assert Image.new("I", (1, 1)).getbands() == ("I",)
    assert Image.new("F", (1, 1)).getbands() == ("F",)
    assert Image.new("P", (1, 1)).getbands() == ("P",)
    assert Image.new("RGB", (1, 1)).getbands() == ("R", "G", "B")
    assert Image.new("RGBA", (1, 1)).getbands() == ("R", "G", "B", "A")
    assert Image.new("CMYK", (1, 1)).getbands() == ("C", "M", "Y", "K")
    assert Image.new("YCbCr", (1, 1)).getbands() == ("Y", "Cb", "Cr")
