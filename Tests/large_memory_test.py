from tester import *

# This test is not run automatically.
#
# It requires > 2gb memory for the >2 gigapixel image generated in the
# second test.  Running this automatically would amount to a denial of
# service on our testing infrastructure.  I expect this test to fail
# on any 32 bit machine, as well as any smallish things (like
# raspberrypis). It does succeed on a 3gb Ubuntu 12.04x64 VM on python
# 2.7 an 3.2

from PIL import Image
ydim = 32769
xdim = 48000
f = tempfile('temp.png')

def _write_png(xdim,ydim):
    im = Image.new('L',(xdim,ydim),(0))
    im.save(f)
    success()

def test_large():
    """ succeeded prepatch"""
    _write_png(xdim,ydim)
def test_2gpx():
    """failed prepatch"""
    _write_png(xdim,xdim)
