from tester import *

from PIL import Image, PyAccess

import test_image_putpixel as put
import test_image_getpixel as get



try:
    import cffi
except:
    skip()

Image.USE_CFFI_ACCESS = True

def test_put():
    put.test_sanity()

def test_get():
    get.test_pixel()
    get.test_image()


