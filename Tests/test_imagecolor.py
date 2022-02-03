import pytest

from PIL import Image, ImageColor


def test_hash():
    # short 3 components
    assert (255, 0, 0) == ImageColor.getrgb("#f00")
    assert (0, 255, 0) == ImageColor.getrgb("#0f0")
    assert (0, 0, 255) == ImageColor.getrgb("#00f")

    # short 4 components
    assert (255, 0, 0, 0) == ImageColor.getrgb("#f000")
    assert (0, 255, 0, 0) == ImageColor.getrgb("#0f00")
    assert (0, 0, 255, 0) == ImageColor.getrgb("#00f0")
    assert (0, 0, 0, 255) == ImageColor.getrgb("#000f")

    # long 3 components
    assert (222, 0, 0) == ImageColor.getrgb("#de0000")
    assert (0, 222, 0) == ImageColor.getrgb("#00de00")
    assert (0, 0, 222) == ImageColor.getrgb("#0000de")

    # long 4 components
    assert (222, 0, 0, 0) == ImageColor.getrgb("#de000000")
    assert (0, 222, 0, 0) == ImageColor.getrgb("#00de0000")
    assert (0, 0, 222, 0) == ImageColor.getrgb("#0000de00")
    assert (0, 0, 0, 222) == ImageColor.getrgb("#000000de")

    # case insensitivity
    assert ImageColor.getrgb("#DEF") == ImageColor.getrgb("#def")
    assert ImageColor.getrgb("#CDEF") == ImageColor.getrgb("#cdef")
    assert ImageColor.getrgb("#DEFDEF") == ImageColor.getrgb("#defdef")
    assert ImageColor.getrgb("#CDEFCDEF") == ImageColor.getrgb("#cdefcdef")

    # not a number
    with pytest.raises(ValueError):
        ImageColor.getrgb("#fo0")
    with pytest.raises(ValueError):
        ImageColor.getrgb("#fo00")
    with pytest.raises(ValueError):
        ImageColor.getrgb("#fo0000")
    with pytest.raises(ValueError):
        ImageColor.getrgb("#fo000000")

    # wrong number of components
    with pytest.raises(ValueError):
        ImageColor.getrgb("#f0000")
    with pytest.raises(ValueError):
        ImageColor.getrgb("#f000000")
    with pytest.raises(ValueError):
        ImageColor.getrgb("#f00000000")
    with pytest.raises(ValueError):
        ImageColor.getrgb("#f000000000")
    with pytest.raises(ValueError):
        ImageColor.getrgb("#f00000 ")


def test_colormap():
    assert (0, 0, 0) == ImageColor.getrgb("black")
    assert (255, 255, 255) == ImageColor.getrgb("white")
    assert (255, 255, 255) == ImageColor.getrgb("WHITE")

    with pytest.raises(ValueError):
        ImageColor.getrgb("black ")


def test_functions():
    # rgb numbers
    assert (255, 0, 0) == ImageColor.getrgb("rgb(255,0,0)")
    assert (0, 255, 0) == ImageColor.getrgb("rgb(0,255,0)")
    assert (0, 0, 255) == ImageColor.getrgb("rgb(0,0,255)")

    # percents
    assert (255, 0, 0) == ImageColor.getrgb("rgb(100%,0%,0%)")
    assert (0, 255, 0) == ImageColor.getrgb("rgb(0%,100%,0%)")
    assert (0, 0, 255) == ImageColor.getrgb("rgb(0%,0%,100%)")

    # rgba numbers
    assert (255, 0, 0, 0) == ImageColor.getrgb("rgba(255,0,0,0)")
    assert (0, 255, 0, 0) == ImageColor.getrgb("rgba(0,255,0,0)")
    assert (0, 0, 255, 0) == ImageColor.getrgb("rgba(0,0,255,0)")
    assert (0, 0, 0, 255) == ImageColor.getrgb("rgba(0,0,0,255)")

    assert (255, 0, 0) == ImageColor.getrgb("hsl(0,100%,50%)")
    assert (255, 0, 0) == ImageColor.getrgb("hsl(360,100%,50%)")
    assert (0, 255, 255) == ImageColor.getrgb("hsl(180,100%,50%)")

    assert (255, 0, 0) == ImageColor.getrgb("hsv(0,100%,100%)")
    assert (255, 0, 0) == ImageColor.getrgb("hsv(360,100%,100%)")
    assert (0, 255, 255) == ImageColor.getrgb("hsv(180,100%,100%)")

    # alternate format
    assert ImageColor.getrgb("hsb(0,100%,50%)") == ImageColor.getrgb("hsv(0,100%,50%)")

    # floats
    assert (254, 3, 3) == ImageColor.getrgb("hsl(0.1,99.2%,50.3%)")
    assert (255, 0, 0) == ImageColor.getrgb("hsl(360.,100.0%,50%)")

    assert (253, 2, 2) == ImageColor.getrgb("hsv(0.1,99.2%,99.3%)")
    assert (255, 0, 0) == ImageColor.getrgb("hsv(360.,100.0%,100%)")

    # case insensitivity
    assert ImageColor.getrgb("RGB(255,0,0)") == ImageColor.getrgb("rgb(255,0,0)")
    assert ImageColor.getrgb("RGB(100%,0%,0%)") == ImageColor.getrgb("rgb(100%,0%,0%)")
    assert ImageColor.getrgb("RGBA(255,0,0,0)") == ImageColor.getrgb("rgba(255,0,0,0)")
    assert ImageColor.getrgb("HSL(0,100%,50%)") == ImageColor.getrgb("hsl(0,100%,50%)")
    assert ImageColor.getrgb("HSV(0,100%,50%)") == ImageColor.getrgb("hsv(0,100%,50%)")
    assert ImageColor.getrgb("HSB(0,100%,50%)") == ImageColor.getrgb("hsb(0,100%,50%)")

    # space agnosticism
    assert (255, 0, 0) == ImageColor.getrgb("rgb(  255  ,  0  ,  0  )")
    assert (255, 0, 0) == ImageColor.getrgb("rgb(  100%  ,  0%  ,  0%  )")
    assert (255, 0, 0, 0) == ImageColor.getrgb("rgba(  255  ,  0  ,  0  ,  0  )")
    assert (255, 0, 0) == ImageColor.getrgb("hsl(  0  ,  100%  ,  50%  )")
    assert (255, 0, 0) == ImageColor.getrgb("hsv(  0  ,  100%  ,  100%  )")

    # wrong number of components
    with pytest.raises(ValueError):
        ImageColor.getrgb("rgb(255,0)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("rgb(255,0,0,0)")

    with pytest.raises(ValueError):
        ImageColor.getrgb("rgb(100%,0%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("rgb(100%,0%,0)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("rgb(100%,0%,0 %)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("rgb(100%,0%,0%,0%)")

    with pytest.raises(ValueError):
        ImageColor.getrgb("rgba(255,0,0)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("rgba(255,0,0,0,0)")

    with pytest.raises(ValueError):
        ImageColor.getrgb("hsl(0,100%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsl(0,100%,0%,0%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsl(0%,100%,50%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsl(0,100,50%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsl(0,100%,50)")

    with pytest.raises(ValueError):
        ImageColor.getrgb("hsv(0,100%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsv(0,100%,0%,0%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsv(0%,100%,50%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsv(0,100,50%)")
    with pytest.raises(ValueError):
        ImageColor.getrgb("hsv(0,100%,50)")


# look for rounding errors (based on code by Tim Hatch)
def test_rounding_errors():
    for color in ImageColor.colormap:
        expected = Image.new("RGB", (1, 1), color).convert("L").getpixel((0, 0))
        actual = ImageColor.getcolor(color, "L")
        assert expected == actual

    assert (0, 255, 115) == ImageColor.getcolor("rgba(0, 255, 115, 33)", "RGB")
    Image.new("RGB", (1, 1), "white")

    assert (0, 0, 0, 255) == ImageColor.getcolor("black", "RGBA")
    assert (255, 255, 255, 255) == ImageColor.getcolor("white", "RGBA")
    assert (0, 255, 115, 33) == ImageColor.getcolor("rgba(0, 255, 115, 33)", "RGBA")
    Image.new("RGBA", (1, 1), "white")

    assert 0 == ImageColor.getcolor("black", "L")
    assert 255 == ImageColor.getcolor("white", "L")
    assert 163 == ImageColor.getcolor("rgba(0, 255, 115, 33)", "L")
    Image.new("L", (1, 1), "white")

    assert 0 == ImageColor.getcolor("black", "1")
    assert 255 == ImageColor.getcolor("white", "1")
    # The following test is wrong, but is current behavior
    # The correct result should be 255 due to the mode 1
    assert 163 == ImageColor.getcolor("rgba(0, 255, 115, 33)", "1")
    # Correct behavior
    # assert
    #     255, ImageColor.getcolor("rgba(0, 255, 115, 33)", "1"))
    Image.new("1", (1, 1), "white")

    assert (0, 255) == ImageColor.getcolor("black", "LA")
    assert (255, 255) == ImageColor.getcolor("white", "LA")
    assert (163, 33) == ImageColor.getcolor("rgba(0, 255, 115, 33)", "LA")
    Image.new("LA", (1, 1), "white")


def test_color_too_long():
    # Arrange
    color_too_long = "hsl(" + "1" * 40 + "," + "1" * 40 + "%," + "1" * 40 + "%)"

    # Act / Assert
    with pytest.raises(ValueError):
        ImageColor.getrgb(color_too_long)
