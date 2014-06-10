from tester import *

from PIL import Image

def test_white():
    i = Image.open('Tests/images/lab.tif')

    bits = i.load()
    
    assert_equal(i.mode, 'LAB')

    assert_equal(i.getbands(), ('L','A', 'B'))

    k = i.getpixel((0,0))
    assert_equal(k, (255,128,128))

    L  = i.getdata(0)
    a = i.getdata(1)
    b = i.getdata(2)

    assert_equal(list(L), [255]*100)
    assert_equal(list(a), [128]*100)
    assert_equal(list(b), [128]*100)
    

def test_green():
    # l= 50 (/100), a = -100 (-128 .. 128) b=0 in PS
    # == RGB: 0, 152, 117
    i = Image.open('Tests/images/lab-green.tif')

    k = i.getpixel((0,0))
    assert_equal(k, (128,28,128))


def test_red():
    # l= 50 (/100), a = 100 (-128 .. 128) b=0 in PS
    # == RGB: 255, 0, 124
    i = Image.open('Tests/images/lab-red.tif')

    k = i.getpixel((0,0))
    assert_equal(k, (128,228,128))
