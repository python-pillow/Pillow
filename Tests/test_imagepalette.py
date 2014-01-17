from tester import *

from PIL import Image
from PIL import ImagePalette

ImagePalette = ImagePalette.ImagePalette

def test_sanity():

    assert_no_exception(lambda: ImagePalette("RGB", list(range(256))*3))
    assert_exception(ValueError, lambda: ImagePalette("RGB", list(range(256))*2))

def test_getcolor():

    palette = ImagePalette()

    map = {}
    for i in range(256):
        map[palette.getcolor((i, i, i))] = i

    assert_equal(len(map), 256)
    assert_exception(ValueError, lambda: palette.getcolor((1, 2, 3)))

def test_file():

    palette = ImagePalette()

    file = tempfile("temp.lut")

    palette.save(file)

    from PIL.ImagePalette import load, raw

    p = load(file)

    # load returns raw palette information
    assert_equal(len(p[0]), 768)
    assert_equal(p[1], "RGB")

    p = raw(p[1], p[0])
    assert_true(isinstance(p, ImagePalette))



