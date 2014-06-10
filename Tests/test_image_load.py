from tester import *

from PIL import Image

import os

def test_sanity():

    im = lena()

    pix = im.load()

    assert_equal(pix[0, 0], (223, 162, 133))

def test_close():    
    im = Image.open("Images/lena.gif")
    assert_no_exception(lambda: im.close())
    assert_exception(ValueError, lambda: im.load())
    assert_exception(ValueError, lambda: im.getpixel((0,0)))

def test_contextmanager():
    fn = None
    with Image.open("Images/lena.gif") as im:
        fn = im.fp.fileno()
        assert_no_exception(lambda: os.fstat(fn))

    assert_exception(OSError, lambda: os.fstat(fn))    
