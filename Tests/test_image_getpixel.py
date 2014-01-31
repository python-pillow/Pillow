from tester import *

from PIL import Image

Image.USE_CFFI_ACCESS=False

def color(mode):
    bands = Image.getmodebands(mode)
    if bands == 1:
        return 1
    else:
        return tuple(range(1, bands+1))



def check(mode, c=None):
    if not c:
        c = color(mode)
        
    #check putpixel
    im = Image.new(mode, (1, 1), None)
    im.putpixel((0, 0), c)
    assert_equal(im.getpixel((0, 0)), c,
                 "put/getpixel roundtrip failed for mode %s, color %s" %
                 (mode, c))
    
    # check inital color
    im = Image.new(mode, (1, 1), c)
    assert_equal(im.getpixel((0, 0)), c,
                 "initial color failed for mode %s, color %s " %
                 (mode, color))

def test_basic():    
    for mode in ("1", "L", "LA", "I", "I;16", "I;16B", "F",
                 "P", "PA", "RGB", "RGBA", "RGBX", "CMYK","YCbCr"):
        check(mode)

def test_signedness():
    # see https://github.com/python-imaging/Pillow/issues/452
    # pixelaccess is using signed int* instead of uint*
    for mode in ("I;16", "I;16B"):
        check(mode, 2**15-1)
        check(mode, 2**15)
        check(mode, 2**15+1)
        check(mode, 2**16-1)

                


