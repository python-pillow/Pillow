from tester import *

# not running this test by default. No DOS against travis.

from PIL import PyAccess

import time

def iterate_get(size, access):
    (w,h) = size
    for x in range(w):
        for y in range(h):
            access[(x,y)]

def iterate_set(size, access):
    (w,h) = size
    for x in range(w):
        for y in range(h):
            access[(x,y)] = access[(x,y)]

def timer(func, label, *args):
    starttime = time.time()
    func(*args)
    endtime = time.time()
    print ("%s: %.4f s" %(label, endtime-starttime))

def test_direct():
    im = lena()
    im.load()
    caccess = im.im.pixel_access(False)
    access = PyAccess.new(im, False)

    assert_equal(caccess[(0,0)], access[(0,0)])

    print ("Size: %sx%s" % im.size)
    timer(iterate_get, 'PyAccess - get', im.size, access)
    timer(iterate_set, 'PyAccess - set', im.size, access)
    timer(iterate_get, 'C-api - get', im.size, caccess)
    timer(iterate_set, 'C-api - set', im.size, caccess)
    
    

    
