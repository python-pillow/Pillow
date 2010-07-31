#!/usr/bin/env python

#
# Shows how to scan a 16 bit grayscale image into a numarray object
#

# Get the path set up to find PIL modules if not installed yet:
import sys ; sys.path.append('../PIL')

from numarray import *
import sane
import Image

def toImage(arr):
    if arr.type().bytes == 1:
        # need to swap coordinates btw array and image (with [::-1])
        im = Image.fromstring('L', arr.shape[::-1], arr.tostring())
    else:
        arr_c = arr - arr.min()
        arr_c *= (255./arr_c.max())
        arr = arr_c.astype(UInt8)
        # need to swap coordinates btw array and image (with [::-1])
        im = Image.fromstring('L', arr.shape[::-1], arr.tostring())
    return im

print 'SANE version:', sane.init()
print 'Available devices=', sane.get_devices()

s = sane.open(sane.get_devices()[0][0])

# Set scan parameters
s.mode = 'gray'
s.br_x=320. ; s.br_y=240.

print 'Device parameters:', s.get_parameters()

s.depth=16
arr16 = s.arr_scan()
toImage(arr16).show()
