from tester import *

from PIL import Image
from PIL import ImageColor

# --------------------------------------------------------------------
# sanity

assert_equal((255, 0, 0), ImageColor.getrgb("#f00"))
assert_equal((255, 0, 0), ImageColor.getrgb("#ff0000"))
assert_equal((255, 0, 0), ImageColor.getrgb("rgb(255,0,0)"))
assert_equal((255, 0, 0), ImageColor.getrgb("rgb(100%,0%,0%)"))
assert_equal((255, 0, 0), ImageColor.getrgb("hsl(0, 100%, 50%)"))
assert_equal((255, 0, 0), ImageColor.getrgb("red"))

# --------------------------------------------------------------------
# look for rounding errors (based on code by Tim Hatch)

for color in list(ImageColor.colormap.keys()):
    expected = Image.new("RGB", (1, 1), color).convert("L").getpixel((0, 0))
    actual = Image.new("L", (1, 1), color).getpixel((0, 0))
    assert_equal(expected, actual)

assert_equal((0, 0, 0), ImageColor.getcolor("black", "RGB"))
assert_equal((255, 255, 255), ImageColor.getcolor("white", "RGB"))

assert_equal(0, ImageColor.getcolor("black", "L"))
assert_equal(255, ImageColor.getcolor("white", "L"))

assert_equal(0, ImageColor.getcolor("black", "1"))
assert_equal(255, ImageColor.getcolor("white", "1"))
