from tester import *

from PIL import Image

def test_sanity():
    i = Image.open('Tests/images/lab.tif')

    bits = i.load()
    
    assert_equal(i.mode, 'LAB')

    assert_equal(i.getbands(), ('L','A', 'B'))

    k = i.getpixel((0,0))
    assert_equal(k, (255,0,0))

    L  = i.getdata(0)
    a = i.getdata(1)
    b = i.getdata(2)

    assert_equal(list(L), [255]*100)
    assert_equal(list(a), [0]*100)
    assert_equal(list(b), [0]*100)
    

