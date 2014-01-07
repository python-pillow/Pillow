#
# The Python Imaging Library
# Pillow fork
#
# Python implementation of the PixelAccess Object
#
# Copyright (c) 1997-2009 by Secret Labs AB.  All rights reserved.
# Copyright (c) 1995-2009 by Fredrik Lundh.
# Copyright (c) 2013 Eric Soroos
#
# See the README file for information on usage and redistribution
#

# Notes:
#
#  * Implements the pixel access object following Access.
#  * Does not implement the line functions, as they don't appear to be used
#  * Taking only the tuple form, which is used from python.
#    * Fill.c uses the integer form, but it's still going to use the old Access.c implementation.
#

from __future__ import print_function

from cffi import FFI

DEBUG = 0
    
defs = """
struct Pixel_RGBA {
    unsigned char r,g,b,a;
};

"""
ffi = FFI()
ffi.cdef(defs)


class PyAccess(object):
    
    def __init__(self, img, readonly = False):
        vals = dict(img.im.unsafe_ptrs)
        self.readonly = readonly
        self.image8 = ffi.cast('unsigned char **', vals['image8'])
        self.image32 = ffi.cast('int **', vals['image32'])
        self.image = ffi.cast('unsigned char **', vals['image'])
        self.xsize = vals['xsize']
        self.ysize = vals['ysize']
        
        if DEBUG:
            print (vals)
        self._post_init()

    def _post_init(): pass
        
    def __setitem__(self, xy, color):
        """
        Modifies the pixel at x,y. The color is given as a single
        numerical value for single band images, and a tuple for
        multi-band images

        :param xy: The pixel coordinate, given as (x, y).
        :param value: The pixel value.                
        """
        if self.readonly: raise ValueError('Attempt to putpixel a read only image') 
        (x,y) = self.check_xy(xy)
        return self.set_pixel(x,y,color)

    def __getitem__(self, xy):
        """
        Returns the pixel at x,y. The pixel is returned as a single
        value for single band images or a tuple for multiple band
        images

        :param xy: The pixel coordinate, given as (x, y).
        """
        
        (x,y) = self.check_xy(xy)
        return self.get_pixel(x,y)

    putpixel = __setitem__
    getpixel = __getitem__

    def check_xy(self, xy):
        (x,y) = xy
        if not (0 <= x < self.xsize and 0 <= y < self.ysize):
            raise ValueError('pixel location out of range')
        return xy


class _PyAccess32_3(PyAccess):
    def _post_init(self, *args, **kwargs):
        self.pixels = ffi.cast("struct Pixel_RGBA **", self.image32)
        
    def get_pixel(self, x,y):
        pixel = self.pixels[y][x]
        return (pixel.r, pixel.g, pixel.b)

    def set_pixel(self, x,y, color):
        pixel = self.pixels[y][x]
        # tuple
        pixel.r, pixel.g, pixel.b = color


class _PyAccess32_4(PyAccess):
    def _post_init(self, *args, **kwargs):
        self.pixels = ffi.cast("struct Pixel_RGBA **", self.image32)
        
    def get_pixel(self, x,y):
        pixel = self.pixels[y][x]
        return (pixel.r, pixel.g, pixel.b, pixel.a)

    def set_pixel(self, x,y, color):
        pixel = self.pixels[y][x]
        # tuple
        #undone clamp?
        pixel.r, pixel.g, pixel.b, pixel.a = color
            
class _PyAccess8(PyAccess):
    def _post_init(self, *args, **kwargs):
        self.pixels = self.image8
        
    def get_pixel(self, x,y):
        return self.pixels[y][x]

    def set_pixel(self, x,y, color):
        try:
            # integer
            self.pixels[y][x] = min(color,255)
        except:
            # tuple
            self.pixels[y][x] = min(color[0],255)


mode_map = {'1': _PyAccess8,
            'L': _PyAccess8,
            'P': _PyAccess8,
            'RGB': _PyAccess32_3,
            'LAB': _PyAccess32_3,
            'YCbCr': _PyAccess32_3,
            'RGBA': _PyAccess32_4,
            'RGBa': _PyAccess32_4,
            'RGBX': _PyAccess32_4,
            'CMYK': _PyAccess32_4,
            }

def new(img, readonly=False):

    access_type = mode_map.get(img.mode, None)
    if not access_type:
        if DEBUG: print ("PyAccess Not Implemented: %s" % img.mode)
        return None
    if DEBUG: print ("New PyAccess: %s" % img.mode)
    return access_type(img, readonly)
    

