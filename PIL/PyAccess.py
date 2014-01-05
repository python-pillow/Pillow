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
struct ImagingMemoryInstance {

    /* Format */
    char mode[7];	/* Band names ("1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "BGR;xy") */
    int type;		/* Data type (IMAGING_TYPE_*) */
    int depth;		/* Depth (ignored in this version) */
    int bands;		/* Number of bands (1, 2, 3, or 4) */
    int xsize;		/* Image dimension. */
    int ysize;

    /* Colour palette (for "P" images only) */
    void *palette;

    /* Data pointers */
    unsigned char **image8;	/* Set for 8-bit images (pixelsize=1). */
    int **image32;	/* Set for 32-bit images (pixelsize=4). */

    /* Internals */
    char **image;	/* Actual raster data. */
    char *block;	/* Set if data is allocated in a single block. */

    int pixelsize;	/* Size of a pixel, in bytes (1, 2 or 4) */
    int linesize;	/* Size of a line, in bytes (xsize * pixelsize) */

    /* Virtual methods */
    void (*destroy)(int im); /*keeping this for compatibility */
};

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
        for att in ['palette', 'image8', 'image32','image', 'block', 'destroy']:
            vals[att] = ffi.cast("void *", vals[att])
        if DEBUG:
            print (vals)
        self.im = ffi.new("struct ImagingMemoryInstance *", vals)

    def __setitem__(self, xy, color):
        """
        Modifies the pixel at x,y. The color is given as a single
        numerical value for single band images, and a tuple for
        multi-band images

        :param xy: The pixel coordinate, given as (x, y).
        :param value: The pixel value.                
        """
        if self.readonly: raise Exception('ValueError')  # undone, ImagingError_ValueError
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
        if not (0 <= x < self.im.xsize and 0 <= y < self.im.ysize):
            raise Exception('ValueError- pixel location out of range') #undone
        return (x,y)


class _PyAccess32_3(PyAccess):
    def __init__(self, *args, **kwargs):
        PyAccess.__init__(self, *args, **kwargs)
        self.pixels = ffi.cast("struct Pixel_RGBA **", self.im.image32)
        
    def get_pixel(self, x,y):
        pixel = self.pixels[y][x]
        return (pixel.r, pixel.g, pixel.b)

    def set_pixel(self, x,y, color):
        pixel = self.pixels[y][x]
        try:
            # tuple
            pixel.r, pixel.g, pixel.b = color
        except:
            # int, as a char[4]
            pixel.r = color >> 24
            pixel.g = (color >> 16) & 0xFF
            pixel.b = (color >> 8) & 0xFF

class _PyAccess32_4(PyAccess):
    def __init__(self, *args, **kwargs):
        PyAccess.__init__(self, *args, **kwargs)
        self.pixels = ffi.cast("struct Pixel_RGBA **", self.im.image32)
        
    def get_pixel(self, x,y):
        pixel = self.pixels[y][x]
        return (pixel.r, pixel.g, pixel.b, pixel.a)

    def set_pixel(self, x,y, color):
        pixel = self.pixels[y][x]
        try:
            # tuple
            pixel.r, pixel.g, pixel.b, pixel.a = color
        except:
            # int, as a char[4]
            pixel.r = color >> 24
            pixel.g = (color >> 16) & 0xFF
            pixel.b = (color >> 8) & 0xFF
            pixel.a = color & 0xFF
            
class _PyAccess8(PyAccess):
    def __init__(self, *args, **kwargs):
        PyAccess.__init__(self, *args, **kwargs)
        self.pixels = self.im.image8
        
    def get_pixel(self, x,y):
        return self.pixels[y][x]

    def set_pixel(self, x,y, color):
        try:
            # integer
            self.pixels[y][x] = color & 0xFF
        except:
            # tuple
            self.pixels[y][x] = color[0] & 0xFF


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
    

