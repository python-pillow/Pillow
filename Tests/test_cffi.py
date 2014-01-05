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


def xtest_direct():
    im = Image.open('lena.png')
    caccess = im.im.pixel_access(false)
    access = PyAccess.new(im)

    print (caccess[(0,0)])
    print (access[(0,0)])
    
    print (access.im.depth)
    print (access.im.image32[0][0])
    print (im.getpixel((0,0)))
    print (access.get_pixel(0,0))
    access.set_pixel(0,0,(1,2,3))
    print (im.getpixel((0,0)))
    print (access.get_pixel(0,0))

    access.set_pixel(0,0,(1,2,3))
    print (im.getpixel((0,0)))
    print (access.get_pixel(0,0))
    
    p_int = (5 << 24) + (4<<16) + (3 <<8)
    access.set_pixel(0,0,p_int)
    print (im.getpixel((0,0)))
    print (access.get_pixel(0,0))
