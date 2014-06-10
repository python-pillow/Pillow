from tester import *

from PIL import Image
from PIL import ImageColor

# --------------------------------------------------------------------
# sanity

assert_equal((255, 0, 0), ImageColor.getrgb("#f00"))
assert_equal((255, 0, 0), ImageColor.getrgb("#ff0000"))
assert_equal((255, 0, 0), ImageColor.getrgb("rgb(255,0,0)"))
assert_equal((255, 0, 0), ImageColor.getrgb("rgb(255, 0, 0)"))
assert_equal((255, 0, 0), ImageColor.getrgb("rgb(100%,0%,0%)"))
assert_equal((255, 0, 0), ImageColor.getrgb("hsl(0, 100%, 50%)"))
assert_equal((255, 0, 0, 0), ImageColor.getrgb("rgba(255,0,0,0)"))
assert_equal((255, 0, 0, 0), ImageColor.getrgb("rgba(255, 0, 0, 0)"))
assert_equal((255, 0, 0), ImageColor.getrgb("red"))

# --------------------------------------------------------------------
# look for rounding errors (based on code by Tim Hatch)

for color in list(ImageColor.colormap.keys()):
    expected = Image.new("RGB", (1, 1), color).convert("L").getpixel((0, 0))
    actual = Image.new("L", (1, 1), color).getpixel((0, 0))
    assert_equal(expected, actual)

assert_equal((0, 0, 0), ImageColor.getcolor("black", "RGB"))
assert_equal((255, 255, 255), ImageColor.getcolor("white", "RGB"))
assert_equal((0, 255, 115), ImageColor.getcolor("rgba(0, 255, 115, 33)", "RGB"))
Image.new("RGB", (1, 1), "white")

assert_equal((0, 0, 0, 255), ImageColor.getcolor("black", "RGBA"))
assert_equal((255, 255, 255, 255), ImageColor.getcolor("white", "RGBA"))
assert_equal((0, 255, 115, 33), ImageColor.getcolor("rgba(0, 255, 115, 33)", "RGBA"))
Image.new("RGBA", (1, 1), "white")

assert_equal(0, ImageColor.getcolor("black", "L"))
assert_equal(255, ImageColor.getcolor("white", "L"))
assert_equal(162, ImageColor.getcolor("rgba(0, 255, 115, 33)", "L"))
Image.new("L", (1, 1), "white")

assert_equal(0, ImageColor.getcolor("black", "1"))
assert_equal(255, ImageColor.getcolor("white", "1"))
# The following test is wrong, but is current behavior
# The correct result should be 255 due to the mode 1 
assert_equal(162, ImageColor.getcolor("rgba(0, 255, 115, 33)", "1"))
# Correct behavior
# assert_equal(255, ImageColor.getcolor("rgba(0, 255, 115, 33)", "1"))
Image.new("1", (1, 1), "white")

assert_equal((0, 255), ImageColor.getcolor("black", "LA"))
assert_equal((255, 255), ImageColor.getcolor("white", "LA"))
assert_equal((162, 33), ImageColor.getcolor("rgba(0, 255, 115, 33)", "LA"))
Image.new("LA", (1, 1), "white")
