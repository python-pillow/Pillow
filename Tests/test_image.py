from tester import *

from PIL import Image

def test_sanity():

    im = Image.new("L", (100, 100))
    assert_equal(repr(im)[:45], "<PIL.Image.Image image mode=L size=100x100 at")
    assert_equal(im.mode, "L")
    assert_equal(im.size, (100, 100))

    im = Image.new("RGB", (100, 100))
    assert_equal(repr(im)[:45], "<PIL.Image.Image image mode=RGB size=100x100 ")
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (100, 100))

    im1 = Image.new("L", (100, 100), None)
    im2 = Image.new("L", (100, 100), 0)
    im3 = Image.new("L", (100, 100), "black")

    assert_equal(im2.getcolors(), [(10000, 0)])
    assert_equal(im3.getcolors(), [(10000, 0)])

    assert_exception(ValueError, lambda: Image.new("X", (100, 100)))
    # assert_exception(MemoryError, lambda: Image.new("L", (1000000, 1000000)))

def test_internals():

    im = Image.new("L", (100, 100))
    im.readonly = 1
    im._copy()
    assert_false(im.readonly)

    im.readonly = 1
    im.paste(0, (0, 0, 100, 100))
    assert_false(im.readonly)

    file = tempfile("temp.ppm")
    im._dump(file)
