from tester import *

from PIL import Image
from PIL import ImageMode

ImageMode.getmode("1")
ImageMode.getmode("L")
ImageMode.getmode("P")
ImageMode.getmode("RGB")
ImageMode.getmode("I")
ImageMode.getmode("F")

m = ImageMode.getmode("1")
assert_equal(m.mode, "1")
assert_equal(m.bands, ("1",))
assert_equal(m.basemode, "L")
assert_equal(m.basetype, "L")

m = ImageMode.getmode("RGB")
assert_equal(m.mode, "RGB")
assert_equal(m.bands, ("R", "G", "B"))
assert_equal(m.basemode, "RGB")
assert_equal(m.basetype, "L")
