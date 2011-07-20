#
# The Python Imaging Library.
# $Id$
#
# the Image class wrapper
#
# partial release history:
# 1995-09-09 fl   Created
# 1996-03-11 fl   PIL release 0.0 (proof of concept)
# 1996-04-30 fl   PIL release 0.1b1
# 1999-07-28 fl   PIL release 1.0 final
# 2000-06-07 fl   PIL release 1.1
# 2000-10-20 fl   PIL release 1.1.1
# 2001-05-07 fl   PIL release 1.1.2
# 2002-03-15 fl   PIL release 1.1.3
# 2003-05-10 fl   PIL release 1.1.4
# 2005-03-28 fl   PIL release 1.1.5
# 2006-12-02 fl   PIL release 1.1.6
# 2009-11-15 fl   PIL release 1.1.7
#
# Copyright (c) 1997-2009 by Secret Labs AB.  All rights reserved.
# Copyright (c) 1995-2009 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

VERSION = "1.1.7"

try:
    import warnings
except ImportError:
    warnings = None

class _imaging_not_installed:
    # module placeholder
    def __getattr__(self, id):
        raise ImportError("The _imaging C module is not installed")

try:
    # give Tk a chance to set up the environment, in case we're
    # using an _imaging module linked against libtcl/libtk (use
    # __import__ to hide this from naive packagers; we don't really
    # depend on Tk unless ImageTk is used, and that module already
    # imports Tkinter)
    __import__("FixTk")
except ImportError:
    pass

try:
    # If the _imaging C module is not present, you can still use
    # the "open" function to identify files, but you cannot load
    # them.  Note that other modules should not refer to _imaging
    # directly; import Image and use the Image.core variable instead.
    import _imaging
    core = _imaging
    del _imaging
except ImportError, v:
    core = _imaging_not_installed()
    if str(v)[:20] == "Module use of python" and warnings:
        # The _imaging C module is present, but not compiled for
        # the right version (windows only).  Print a warning, if
        # possible.
        warnings.warn(
            "The _imaging extension was built for another version "
            "of Python; most PIL functions will be disabled",
            RuntimeWarning
            )

import ImageMode
import ImagePalette

import os, string, sys

# type stuff
from types import IntType, StringType, TupleType

try:
    UnicodeStringType = type(unicode(""))
    ##
    # (Internal) Checks if an object is a string.  If the current
    # Python version supports Unicode, this checks for both 8-bit
    # and Unicode strings.
    def isStringType(t):
        return isinstance(t, StringType) or isinstance(t, UnicodeStringType)
except NameError:
    def isStringType(t):
        return isinstance(t, StringType)

##
# (Internal) Checks if an object is a tuple.

def isTupleType(t):
    return isinstance(t, TupleType)

##
# (Internal) Checks if an object is an image object.

def isImageType(t):
    return hasattr(t, "im")

##
# (Internal) Checks if an object is a string, and that it points to a
# directory.

def isDirectory(f):
    return isStringType(f) and os.path.isdir(f)

from operator import isNumberType, isSequenceType

#
# Debug level

DEBUG = 0

#
# Constants (also defined in _imagingmodule.c!)

NONE = 0

# transpose
FLIP_LEFT_RIGHT = 0
FLIP_TOP_BOTTOM = 1
ROTATE_90 = 2
ROTATE_180 = 3
ROTATE_270 = 4

# transforms
AFFINE = 0
EXTENT = 1
PERSPECTIVE = 2
QUAD = 3
MESH = 4

# resampling filters
NONE = 0
NEAREST = 0
ANTIALIAS = 1 # 3-lobed lanczos
LINEAR = BILINEAR = 2
CUBIC = BICUBIC = 3

# dithers
NONE = 0
NEAREST = 0
ORDERED = 1 # Not yet implemented
RASTERIZE = 2 # Not yet implemented
FLOYDSTEINBERG = 3 # default

# palettes/quantizers
WEB = 0
ADAPTIVE = 1

# categories
NORMAL = 0
SEQUENCE = 1
CONTAINER = 2

# --------------------------------------------------------------------
# Registries

ID = []
OPEN = {}
MIME = {}
SAVE = {}
EXTENSION = {}

# --------------------------------------------------------------------
# Modes supported by this version

_MODEINFO = {
    # NOTE: this table will be removed in future versions.  use
    # getmode* functions or ImageMode descriptors instead.

    # official modes
    "1": ("L", "L", ("1",)),
    "L": ("L", "L", ("L",)),
    "I": ("L", "I", ("I",)),
    "F": ("L", "F", ("F",)),
    "P": ("RGB", "L", ("P",)),
    "RGB": ("RGB", "L", ("R", "G", "B")),
    "RGBX": ("RGB", "L", ("R", "G", "B", "X")),
    "RGBA": ("RGB", "L", ("R", "G", "B", "A")),
    "CMYK": ("RGB", "L", ("C", "M", "Y", "K")),
    "YCbCr": ("RGB", "L", ("Y", "Cb", "Cr")),

    # Experimental modes include I;16, I;16L, I;16B, RGBa, BGR;15, and
    # BGR;24.  Use these modes only if you know exactly what you're
    # doing...

}

try:
    byteorder = sys.byteorder
except AttributeError:
    import struct
    if struct.unpack("h", "\0\1")[0] == 1:
        byteorder = "big"
    else:
        byteorder = "little"

if byteorder == 'little':
    _ENDIAN = '<'
else:
    _ENDIAN = '>'

_MODE_CONV = {
    # official modes
    "1": ('|b1', None), # broken
    "L": ('|u1', None),
    "I": (_ENDIAN + 'i4', None),
    "F": (_ENDIAN + 'f4', None),
    "P": ('|u1', None),
    "RGB": ('|u1', 3),
    "RGBX": ('|u1', 4),
    "RGBA": ('|u1', 4),
    "CMYK": ('|u1', 4),
    "YCbCr": ('|u1', 4),
}

def _conv_type_shape(im):
    shape = im.size[1], im.size[0]
    typ, extra = _MODE_CONV[im.mode]
    if extra is None:
        return shape, typ
    else:
        return shape+(extra,), typ


MODES = _MODEINFO.keys()
MODES.sort()

# raw modes that may be memory mapped.  NOTE: if you change this, you
# may have to modify the stride calculation in map.c too!
_MAPMODES = ("L", "P", "RGBX", "RGBA", "CMYK", "I;16", "I;16L", "I;16B")

##
# Gets the "base" mode for given mode.  This function returns "L" for
# images that contain grayscale data, and "RGB" for images that
# contain color data.
#
# @param mode Input mode.
# @return "L" or "RGB".
# @exception KeyError If the input mode was not a standard mode.

def getmodebase(mode):
    return ImageMode.getmode(mode).basemode

##
# Gets the storage type mode.  Given a mode, this function returns a
# single-layer mode suitable for storing individual bands.
#
# @param mode Input mode.
# @return "L", "I", or "F".
# @exception KeyError If the input mode was not a standard mode.

def getmodetype(mode):
    return ImageMode.getmode(mode).basetype

##
# Gets a list of individual band names.  Given a mode, this function
# returns a tuple containing the names of individual bands (use
# {@link #getmodetype} to get the mode used to store each individual
# band.
#
# @param mode Input mode.
# @return A tuple containing band names.  The length of the tuple
#     gives the number of bands in an image of the given mode.
# @exception KeyError If the input mode was not a standard mode.

def getmodebandnames(mode):
    return ImageMode.getmode(mode).bands

##
# Gets the number of individual bands for this mode.
#
# @param mode Input mode.
# @return The number of bands in this mode.
# @exception KeyError If the input mode was not a standard mode.

def getmodebands(mode):
    return len(ImageMode.getmode(mode).bands)

# --------------------------------------------------------------------
# Helpers

_initialized = 0

##
# Explicitly loads standard file format drivers.

def preinit():
    "Load standard file format drivers."

    global _initialized
    if _initialized >= 1:
        return

    try:
        import BmpImagePlugin
    except ImportError:
        pass
    try:
        import GifImagePlugin
    except ImportError:
        pass
    try:
        import JpegImagePlugin
    except ImportError:
        pass
    try:
        import PpmImagePlugin
    except ImportError:
        pass
    try:
        import PngImagePlugin
    except ImportError:
        pass
#   try:
#       import TiffImagePlugin
#   except ImportError:
#       pass

    _initialized = 1

##
# Explicitly initializes the Python Imaging Library.  This function
# loads all available file format drivers.

def init():
    "Load all file format drivers."

    global _initialized
    if _initialized >= 2:
        return 0

    visited = {}

    directories = sys.path

    try:
        directories = directories + [os.path.dirname(__file__)]
    except NameError:
        pass

    # only check directories (including current, if present in the path)
    for directory in filter(isDirectory, directories):
        fullpath = os.path.abspath(directory)
        if visited.has_key(fullpath):
            continue
        for file in os.listdir(directory):
            if file[-14:] == "ImagePlugin.py":
                f, e = os.path.splitext(file)
                try:
                    sys.path.insert(0, directory)
                    try:
                        __import__(f, globals(), locals(), [])
                    finally:
                        del sys.path[0]
                except ImportError:
                    if DEBUG:
                        print "Image: failed to import",
                        print f, ":", sys.exc_value
        visited[fullpath] = None

    if OPEN or SAVE:
        _initialized = 2
        return 1

# --------------------------------------------------------------------
# Codec factories (used by tostring/fromstring and ImageFile.load)

def _getdecoder(mode, decoder_name, args, extra=()):

    # tweak arguments
    if args is None:
        args = ()
    elif not isTupleType(args):
        args = (args,)

    try:
        # get decoder
        decoder = getattr(core, decoder_name + "_decoder")
        # print decoder, (mode,) + args + extra
        return apply(decoder, (mode,) + args + extra)
    except AttributeError:
        raise IOError("decoder %s not available" % decoder_name)

def _getencoder(mode, encoder_name, args, extra=()):

    # tweak arguments
    if args is None:
        args = ()
    elif not isTupleType(args):
        args = (args,)

    try:
        # get encoder
        encoder = getattr(core, encoder_name + "_encoder")
        # print encoder, (mode,) + args + extra
        return apply(encoder, (mode,) + args + extra)
    except AttributeError:
        raise IOError("encoder %s not available" % encoder_name)


# --------------------------------------------------------------------
# Simple expression analyzer

class _E:
    def __init__(self, data): self.data = data
    def __coerce__(self, other): return self, _E(other)
    def __add__(self, other): return _E((self.data, "__add__", other.data))
    def __mul__(self, other): return _E((self.data, "__mul__", other.data))

def _getscaleoffset(expr):
    stub = ["stub"]
    data = expr(_E(stub)).data
    try:
        (a, b, c) = data # simplified syntax
        if (a is stub and b == "__mul__" and isNumberType(c)):
            return c, 0.0
        if (a is stub and b == "__add__" and isNumberType(c)):
            return 1.0, c
    except TypeError: pass
    try:
        ((a, b, c), d, e) = data # full syntax
        if (a is stub and b == "__mul__" and isNumberType(c) and
            d == "__add__" and isNumberType(e)):
            return c, e
    except TypeError: pass
    raise ValueError("illegal expression")


# --------------------------------------------------------------------
# Implementation wrapper

##
# This class represents an image object.  To create Image objects, use
# the appropriate factory functions.  There's hardly ever any reason
# to call the Image constructor directly.
#
# @see #open
# @see #new
# @see #fromstring

class Image:

    format = None
    format_description = None

    def __init__(self):
        # FIXME: take "new" parameters / other image?
        # FIXME: turn mode and size into delegating properties?
        self.im = None
        self.mode = ""
        self.size = (0, 0)
        self.palette = None
        self.info = {}
        self.category = NORMAL
        self.readonly = 0

    def _new(self, im):
        new = Image()
        new.im = im
        new.mode = im.mode
        new.size = im.size
        new.palette = self.palette
        if im.mode == "P":
            new.palette = ImagePalette.ImagePalette()
        try:
            new.info = self.info.copy()
        except AttributeError:
            # fallback (pre-1.5.2)
            new.info = {}
            for k, v in self.info:
                new.info[k] = v
        return new

    _makeself = _new # compatibility

    def _copy(self):
        self.load()
        self.im = self.im.copy()
        self.readonly = 0

    def _dump(self, file=None, format=None):
        import tempfile
        if not file:
            file = tempfile.mktemp()
        self.load()
        if not format or format == "PPM":
            self.im.save_ppm(file)
        else:
            file = file + "." + format
            self.save(file, format)
        return file

    def __repr__(self):
        return "<%s.%s image mode=%s size=%dx%d at 0x%X>" % (
            self.__class__.__module__, self.__class__.__name__,
            self.mode, self.size[0], self.size[1],
            id(self)
            )

    def __getattr__(self, name):
        if name == "__array_interface__":
            # numpy array interface support
            new = {}
            shape, typestr = _conv_type_shape(self)
            new['shape'] = shape
            new['typestr'] = typestr
            new['data'] = self.tostring()
            return new
        raise AttributeError(name)

    ##
    # Returns a string containing pixel data.
    #
    # @param encoder_name What encoder to use.  The default is to
    #    use the standard "raw" encoder.
    # @param *args Extra arguments to the encoder.
    # @return An 8-bit string.

    def tostring(self, encoder_name="raw", *args):
        "Return image as a binary string"

        # may pass tuple instead of argument list
        if len(args) == 1 and isTupleType(args[0]):
            args = args[0]

        if encoder_name == "raw" and args == ():
            args = self.mode

        self.load()

        # unpack data
        e = _getencoder(self.mode, encoder_name, args)
        e.setimage(self.im)

        bufsize = max(65536, self.size[0] * 4) # see RawEncode.c

        data = []
        while 1:
            l, s, d = e.encode(bufsize)
            data.append(d)
            if s:
                break
        if s < 0:
            raise RuntimeError("encoder error %d in tostring" % s)

        return string.join(data, "")

    ##
    # Returns the image converted to an X11 bitmap.  This method
    # only works for mode "1" images.
    #
    # @param name The name prefix to use for the bitmap variables.
    # @return A string containing an X11 bitmap.
    # @exception ValueError If the mode is not "1"

    def tobitmap(self, name="image"):
        "Return image as an XBM bitmap"

        self.load()
        if self.mode != "1":
            raise ValueError("not a bitmap")
        data = self.tostring("xbm")
        return string.join(["#define %s_width %d\n" % (name, self.size[0]),
                "#define %s_height %d\n"% (name, self.size[1]),
                "static char %s_bits[] = {\n" % name, data, "};"], "")

    ##
    # Loads this image with pixel data from a string.
    # <p>
    # This method is similar to the {@link #fromstring} function, but
    # loads data into this image instead of creating a new image
    # object.

    def fromstring(self, data, decoder_name="raw", *args):
        "Load data to image from binary string"

        # may pass tuple instead of argument list
        if len(args) == 1 and isTupleType(args[0]):
            args = args[0]

        # default format
        if decoder_name == "raw" and args == ():
            args = self.mode

        # unpack data
        d = _getdecoder(self.mode, decoder_name, args)
        d.setimage(self.im)
        s = d.decode(data)

        if s[0] >= 0:
            raise ValueError("not enough image data")
        if s[1] != 0:
            raise ValueError("cannot decode image data")

    ##
    # Allocates storage for the image and loads the pixel data.  In
    # normal cases, you don't need to call this method, since the
    # Image class automatically loads an opened image when it is
    # accessed for the first time.
    #
    # @return An image access object.

    def load(self):
        "Explicitly load pixel data."
        if self.im and self.palette and self.palette.dirty:
            # realize palette
            apply(self.im.putpalette, self.palette.getdata())
            self.palette.dirty = 0
            self.palette.mode = "RGB"
            self.palette.rawmode = None
            if self.info.has_key("transparency"):
                self.im.putpalettealpha(self.info["transparency"], 0)
                self.palette.mode = "RGBA"
        if self.im:
            return self.im.pixel_access(self.readonly)

    ##
    # Verifies the contents of a file. For data read from a file, this
    # method attempts to determine if the file is broken, without
    # actually decoding the image data.  If this method finds any
    # problems, it raises suitable exceptions.  If you need to load
    # the image after using this method, you must reopen the image
    # file.

    def verify(self):
        "Verify file contents."
        pass

    ##
    # Returns a converted copy of this image. For the "P" mode, this
    # method translates pixels through the palette.  If mode is
    # omitted, a mode is chosen so that all information in the image
    # and the palette can be represented without a palette.
    # <p>
    # The current version supports all possible conversions between
    # "L", "RGB" and "CMYK."
    # <p>
    # When translating a colour image to black and white (mode "L"),
    # the library uses the ITU-R 601-2 luma transform:
    # <p>
    # <b>L = R * 299/1000 + G * 587/1000 + B * 114/1000</b>
    # <p>
    # When translating a greyscale image into a bilevel image (mode
    # "1"), all non-zero values are set to 255 (white). To use other
    # thresholds, use the {@link #Image.point} method.
    #
    # @def convert(mode, matrix=None, **options)
    # @param mode The requested mode.
    # @param matrix An optional conversion matrix.  If given, this
    #    should be 4- or 16-tuple containing floating point values.
    # @param options Additional options, given as keyword arguments.
    # @keyparam dither Dithering method, used when converting from
    #    mode "RGB" to "P".
    #    Available methods are NONE or FLOYDSTEINBERG (default).
    # @keyparam palette Palette to use when converting from mode "RGB"
    #    to "P".  Available palettes are WEB or ADAPTIVE.
    # @keyparam colors Number of colors to use for the ADAPTIVE palette.
    #    Defaults to 256.
    # @return An Image object.

    def convert(self, mode=None, data=None, dither=None,
                palette=WEB, colors=256):
        "Convert to other pixel format"

        if not mode:
            # determine default mode
            if self.mode == "P":
                self.load()
                if self.palette:
                    mode = self.palette.mode
                else:
                    mode = "RGB"
            else:
                return self.copy()

        self.load()

        if data:
            # matrix conversion
            if mode not in ("L", "RGB"):
                raise ValueError("illegal conversion")
            im = self.im.convert_matrix(mode, data)
            return self._new(im)

        if mode == "P" and palette == ADAPTIVE:
            im = self.im.quantize(colors)
            return self._new(im)

        # colourspace conversion
        if dither is None:
            dither = FLOYDSTEINBERG

        try:
            im = self.im.convert(mode, dither)
        except ValueError:
            try:
                # normalize source image and try again
                im = self.im.convert(getmodebase(self.mode))
                im = im.convert(mode, dither)
            except KeyError:
                raise ValueError("illegal conversion")

        return self._new(im)

    def quantize(self, colors=256, method=0, kmeans=0, palette=None):

        # methods:
        #    0 = median cut
        #    1 = maximum coverage

        # NOTE: this functionality will be moved to the extended
        # quantizer interface in a later version of PIL.

        self.load()

        if palette:
            # use palette from reference image
            palette.load()
            if palette.mode != "P":
                raise ValueError("bad mode for palette image")
            if self.mode != "RGB" and self.mode != "L":
                raise ValueError(
                    "only RGB or L mode images can be quantized to a palette"
                    )
            im = self.im.convert("P", 1, palette.im)
            return self._makeself(im)

        im = self.im.quantize(colors, method, kmeans)
        return self._new(im)

    ##
    # Copies this image. Use this method if you wish to paste things
    # into an image, but still retain the original.
    #
    # @return An Image object.

    def copy(self):
        "Copy raster data"

        self.load()
        im = self.im.copy()
        return self._new(im)

    ##
    # Returns a rectangular region from this image. The box is a
    # 4-tuple defining the left, upper, right, and lower pixel
    # coordinate.
    # <p>
    # This is a lazy operation.  Changes to the source image may or
    # may not be reflected in the cropped image.  To break the
    # connection, call the {@link #Image.load} method on the cropped
    # copy.
    #
    # @param The crop rectangle, as a (left, upper, right, lower)-tuple.
    # @return An Image object.

    def crop(self, box=None):
        "Crop region from image"

        self.load()
        if box is None:
            return self.copy()

        # lazy operation
        return _ImageCrop(self, box)

    ##
    # Configures the image file loader so it returns a version of the
    # image that as closely as possible matches the given mode and
    # size.  For example, you can use this method to convert a colour
    # JPEG to greyscale while loading it, or to extract a 128x192
    # version from a PCD file.
    # <p>
    # Note that this method modifies the Image object in place.  If
    # the image has already been loaded, this method has no effect.
    #
    # @param mode The requested mode.
    # @param size The requested size.

    def draft(self, mode, size):
        "Configure image decoder"

        pass

    def _expand(self, xmargin, ymargin=None):
        if ymargin is None:
            ymargin = xmargin
        self.load()
        return self._new(self.im.expand(xmargin, ymargin, 0))

    ##
    # Filters this image using the given filter.  For a list of
    # available filters, see the <b>ImageFilter</b> module.
    #
    # @param filter Filter kernel.
    # @return An Image object.
    # @see ImageFilter

    def filter(self, filter):
        "Apply environment filter to image"

        self.load()

        if callable(filter):
            filter = filter()
        if not hasattr(filter, "filter"):
            raise TypeError("filter argument should be ImageFilter.Filter instance or class")

        if self.im.bands == 1:
            return self._new(filter.filter(self.im))
        # fix to handle multiband images since _imaging doesn't
        ims = []
        for c in range(self.im.bands):
            ims.append(self._new(filter.filter(self.im.getband(c))))
        return merge(self.mode, ims)

    ##
    # Returns a tuple containing the name of each band in this image.
    # For example, <b>getbands</b> on an RGB image returns ("R", "G", "B").
    #
    # @return A tuple containing band names.

    def getbands(self):
        "Get band names"

        return ImageMode.getmode(self.mode).bands

    ##
    # Calculates the bounding box of the non-zero regions in the
    # image.
    #
    # @return The bounding box is returned as a 4-tuple defining the
    #    left, upper, right, and lower pixel coordinate. If the image
    #    is completely empty, this method returns None.

    def getbbox(self):
        "Get bounding box of actual data (non-zero pixels) in image"

        self.load()
        return self.im.getbbox()

    ##
    # Returns a list of colors used in this image.
    #
    # @param maxcolors Maximum number of colors.  If this number is
    #    exceeded, this method returns None.  The default limit is
    #    256 colors.
    # @return An unsorted list of (count, pixel) values.

    def getcolors(self, maxcolors=256):
        "Get colors from image, up to given limit"

        self.load()
        if self.mode in ("1", "L", "P"):
            h = self.im.histogram()
            out = []
            for i in range(256):
                if h[i]:
                    out.append((h[i], i))
            if len(out) > maxcolors:
                return None
            return out
        return self.im.getcolors(maxcolors)

    ##
    # Returns the contents of this image as a sequence object
    # containing pixel values.  The sequence object is flattened, so
    # that values for line one follow directly after the values of
    # line zero, and so on.
    # <p>
    # Note that the sequence object returned by this method is an
    # internal PIL data type, which only supports certain sequence
    # operations.  To convert it to an ordinary sequence (e.g. for
    # printing), use <b>list(im.getdata())</b>.
    #
    # @param band What band to return.  The default is to return
    #    all bands.  To return a single band, pass in the index
    #    value (e.g. 0 to get the "R" band from an "RGB" image).
    # @return A sequence-like object.

    def getdata(self, band = None):
        "Get image data as sequence object."

        self.load()
        if band is not None:
            return self.im.getband(band)
        return self.im # could be abused

    ##
    # Gets the the minimum and maximum pixel values for each band in
    # the image.
    #
    # @return For a single-band image, a 2-tuple containing the
    #    minimum and maximum pixel value.  For a multi-band image,
    #    a tuple containing one 2-tuple for each band.

    def getextrema(self):
        "Get min/max value"

        self.load()
        if self.im.bands > 1:
            extrema = []
            for i in range(self.im.bands):
                extrema.append(self.im.getband(i).getextrema())
            return tuple(extrema)
        return self.im.getextrema()

    ##
    # Returns a PyCObject that points to the internal image memory.
    #
    # @return A PyCObject object.

    def getim(self):
        "Get PyCObject pointer to internal image memory"

        self.load()
        return self.im.ptr


    ##
    # Returns the image palette as a list.
    #
    # @return A list of color values [r, g, b, ...], or None if the
    #    image has no palette.

    def getpalette(self):
        "Get palette contents."

        self.load()
        try:
            return map(ord, self.im.getpalette())
        except ValueError:
            return None # no palette


    ##
    # Returns the pixel value at a given position.
    #
    # @param xy The coordinate, given as (x, y).
    # @return The pixel value.  If the image is a multi-layer image,
    #    this method returns a tuple.

    def getpixel(self, xy):
        "Get pixel value"

        self.load()
        return self.im.getpixel(xy)

    ##
    # Returns the horizontal and vertical projection.
    #
    # @return Two sequences, indicating where there are non-zero
    #     pixels along the X-axis and the Y-axis, respectively.

    def getprojection(self):
        "Get projection to x and y axes"

        self.load()
        x, y = self.im.getprojection()
        return map(ord, x), map(ord, y)

    ##
    # Returns a histogram for the image. The histogram is returned as
    # a list of pixel counts, one for each pixel value in the source
    # image. If the image has more than one band, the histograms for
    # all bands are concatenated (for example, the histogram for an
    # "RGB" image contains 768 values).
    # <p>
    # A bilevel image (mode "1") is treated as a greyscale ("L") image
    # by this method.
    # <p>
    # If a mask is provided, the method returns a histogram for those
    # parts of the image where the mask image is non-zero. The mask
    # image must have the same size as the image, and be either a
    # bi-level image (mode "1") or a greyscale image ("L").
    #
    # @def histogram(mask=None)
    # @param mask An optional mask.
    # @return A list containing pixel counts.

    def histogram(self, mask=None, extrema=None):
        "Take histogram of image"

        self.load()
        if mask:
            mask.load()
            return self.im.histogram((0, 0), mask.im)
        if self.mode in ("I", "F"):
            if extrema is None:
                extrema = self.getextrema()
            return self.im.histogram(extrema)
        return self.im.histogram()

    ##
    # (Deprecated) Returns a copy of the image where the data has been
    # offset by the given distances. Data wraps around the edges. If
    # yoffset is omitted, it is assumed to be equal to xoffset.
    # <p>
    # This method is deprecated. New code should use the <b>offset</b>
    # function in the <b>ImageChops</b> module.
    #
    # @param xoffset The horizontal distance.
    # @param yoffset The vertical distance.  If omitted, both
    #    distances are set to the same value.
    # @return An Image object.

    def offset(self, xoffset, yoffset=None):
        "(deprecated) Offset image in horizontal and/or vertical direction"
        if warnings:
            warnings.warn(
                "'offset' is deprecated; use 'ImageChops.offset' instead",
                DeprecationWarning, stacklevel=2
                )
        import ImageChops
        return ImageChops.offset(self, xoffset, yoffset)

    ##
    # Pastes another image into this image. The box argument is either
    # a 2-tuple giving the upper left corner, a 4-tuple defining the
    # left, upper, right, and lower pixel coordinate, or None (same as
    # (0, 0)).  If a 4-tuple is given, the size of the pasted image
    # must match the size of the region.
    # <p>
    # If the modes don't match, the pasted image is converted to the
    # mode of this image (see the {@link #Image.convert} method for
    # details).
    # <p>
    # Instead of an image, the source can be a integer or tuple
    # containing pixel values.  The method then fills the region
    # with the given colour.  When creating RGB images, you can
    # also use colour strings as supported by the ImageColor module.
    # <p>
    # If a mask is given, this method updates only the regions
    # indicated by the mask.  You can use either "1", "L" or "RGBA"
    # images (in the latter case, the alpha band is used as mask).
    # Where the mask is 255, the given image is copied as is.  Where
    # the mask is 0, the current value is preserved.  Intermediate
    # values can be used for transparency effects.
    # <p>
    # Note that if you paste an "RGBA" image, the alpha band is
    # ignored.  You can work around this by using the same image as
    # both source image and mask.
    #
    # @param im Source image or pixel value (integer or tuple).
    # @param box An optional 4-tuple giving the region to paste into.
    #    If a 2-tuple is used instead, it's treated as the upper left
    #    corner.  If omitted or None, the source is pasted into the
    #    upper left corner.
    #    <p>
    #    If an image is given as the second argument and there is no
    #    third, the box defaults to (0, 0), and the second argument
    #    is interpreted as a mask image.
    # @param mask An optional mask image.
    # @return An Image object.

    def paste(self, im, box=None, mask=None):
        "Paste other image into region"

        if isImageType(box) and mask is None:
            # abbreviated paste(im, mask) syntax
            mask = box; box = None

        if box is None:
            # cover all of self
            box = (0, 0) + self.size

        if len(box) == 2:
            # lower left corner given; get size from image or mask
            if isImageType(im):
                size = im.size
            elif isImageType(mask):
                size = mask.size
            else:
                # FIXME: use self.size here?
                raise ValueError(
                    "cannot determine region size; use 4-item box"
                    )
            box = box + (box[0]+size[0], box[1]+size[1])

        if isStringType(im):
            import ImageColor
            im = ImageColor.getcolor(im, self.mode)

        elif isImageType(im):
            im.load()
            if self.mode != im.mode:
                if self.mode != "RGB" or im.mode not in ("RGBA", "RGBa"):
                    # should use an adapter for this!
                    im = im.convert(self.mode)
            im = im.im

        self.load()
        if self.readonly:
            self._copy()

        if mask:
            mask.load()
            self.im.paste(im, box, mask.im)
        else:
            self.im.paste(im, box)

    ##
    # Maps this image through a lookup table or function.
    #
    # @param lut A lookup table, containing 256 values per band in the
    #    image. A function can be used instead, it should take a single
    #    argument. The function is called once for each possible pixel
    #    value, and the resulting table is applied to all bands of the
    #    image.
    # @param mode Output mode (default is same as input).  In the
    #    current version, this can only be used if the source image
    #    has mode "L" or "P", and the output has mode "1".
    # @return An Image object.

    def point(self, lut, mode=None):
        "Map image through lookup table"

        self.load()

        if isinstance(lut, ImagePointHandler):
            return lut.point(self)

        if not isSequenceType(lut):
            # if it isn't a list, it should be a function
            if self.mode in ("I", "I;16", "F"):
                # check if the function can be used with point_transform
                scale, offset = _getscaleoffset(lut)
                return self._new(self.im.point_transform(scale, offset))
            # for other modes, convert the function to a table
            lut = map(lut, range(256)) * self.im.bands

        if self.mode == "F":
            # FIXME: _imaging returns a confusing error message for this case
            raise ValueError("point operation not supported for this mode")

        return self._new(self.im.point(lut, mode))

    ##
    # Adds or replaces the alpha layer in this image.  If the image
    # does not have an alpha layer, it's converted to "LA" or "RGBA".
    # The new layer must be either "L" or "1".
    #
    # @param im The new alpha layer.  This can either be an "L" or "1"
    #    image having the same size as this image, or an integer or
    #    other color value.

    def putalpha(self, alpha):
        "Set alpha layer"

        self.load()
        if self.readonly:
            self._copy()

        if self.mode not in ("LA", "RGBA"):
            # attempt to promote self to a matching alpha mode
            try:
                mode = getmodebase(self.mode) + "A"
                try:
                    self.im.setmode(mode)
                except (AttributeError, ValueError):
                    # do things the hard way
                    im = self.im.convert(mode)
                    if im.mode not in ("LA", "RGBA"):
                        raise ValueError # sanity check
                    self.im = im
                self.mode = self.im.mode
            except (KeyError, ValueError):
                raise ValueError("illegal image mode")

        if self.mode == "LA":
            band = 1
        else:
            band = 3

        if isImageType(alpha):
            # alpha layer
            if alpha.mode not in ("1", "L"):
                raise ValueError("illegal image mode")
            alpha.load()
            if alpha.mode == "1":
                alpha = alpha.convert("L")
        else:
            # constant alpha
            try:
                self.im.fillband(band, alpha)
            except (AttributeError, ValueError):
                # do things the hard way
                alpha = new("L", self.size, alpha)
            else:
                return

        self.im.putband(alpha.im, band)

    ##
    # Copies pixel data to this image.  This method copies data from a
    # sequence object into the image, starting at the upper left
    # corner (0, 0), and continuing until either the image or the
    # sequence ends.  The scale and offset values are used to adjust
    # the sequence values: <b>pixel = value*scale + offset</b>.
    #
    # @param data A sequence object.
    # @param scale An optional scale value.  The default is 1.0.
    # @param offset An optional offset value.  The default is 0.0.

    def putdata(self, data, scale=1.0, offset=0.0):
        "Put data from a sequence object into an image."

        self.load()
        if self.readonly:
            self._copy()

        self.im.putdata(data, scale, offset)

    ##
    # Attaches a palette to this image.  The image must be a "P" or
    # "L" image, and the palette sequence must contain 768 integer
    # values, where each group of three values represent the red,
    # green, and blue values for the corresponding pixel
    # index. Instead of an integer sequence, you can use an 8-bit
    # string.
    #
    # @def putpalette(data)
    # @param data A palette sequence (either a list or a string).

    def putpalette(self, data, rawmode="RGB"):
        "Put palette data into an image."

        if self.mode not in ("L", "P"):
            raise ValueError("illegal image mode")
        self.load()
        if isinstance(data, ImagePalette.ImagePalette):
            palette = ImagePalette.raw(data.rawmode, data.palette)
        else:
            if not isStringType(data):
                data = string.join(map(chr, data), "")
            palette = ImagePalette.raw(rawmode, data)
        self.mode = "P"
        self.palette = palette
        self.palette.mode = "RGB"
        self.load() # install new palette

    ##
    # Modifies the pixel at the given position. The colour is given as
    # a single numerical value for single-band images, and a tuple for
    # multi-band images.
    # <p>
    # Note that this method is relatively slow.  For more extensive
    # changes, use {@link #Image.paste} or the <b>ImageDraw</b> module
    # instead.
    #
    # @param xy The pixel coordinate, given as (x, y).
    # @param value The pixel value.
    # @see #Image.paste
    # @see #Image.putdata
    # @see ImageDraw

    def putpixel(self, xy, value):
        "Set pixel value"

        self.load()
        if self.readonly:
            self._copy()

        return self.im.putpixel(xy, value)

    ##
    # Returns a resized copy of this image.
    #
    # @def resize(size, filter=NEAREST)
    # @param size The requested size in pixels, as a 2-tuple:
    #    (width, height).
    # @param filter An optional resampling filter.  This can be
    #    one of <b>NEAREST</b> (use nearest neighbour), <b>BILINEAR</b>
    #    (linear interpolation in a 2x2 environment), <b>BICUBIC</b>
    #    (cubic spline interpolation in a 4x4 environment), or
    #    <b>ANTIALIAS</b> (a high-quality downsampling filter).
    #    If omitted, or if the image has mode "1" or "P", it is
    #    set <b>NEAREST</b>.
    # @return An Image object.

    def resize(self, size, resample=NEAREST):
        "Resize image"

        if resample not in (NEAREST, BILINEAR, BICUBIC, ANTIALIAS):
            raise ValueError("unknown resampling filter")

        self.load()

        if self.mode in ("1", "P"):
            resample = NEAREST

        if resample == ANTIALIAS:
            # requires stretch support (imToolkit & PIL 1.1.3)
            try:
                im = self.im.stretch(size, resample)
            except AttributeError:
                raise ValueError("unsupported resampling filter")
        else:
            im = self.im.resize(size, resample)

        return self._new(im)

    ##
    # Returns a rotated copy of this image.  This method returns a
    # copy of this image, rotated the given number of degrees counter
    # clockwise around its centre.
    #
    # @def rotate(angle, filter=NEAREST)
    # @param angle In degrees counter clockwise.
    # @param filter An optional resampling filter.  This can be
    #    one of <b>NEAREST</b> (use nearest neighbour), <b>BILINEAR</b>
    #    (linear interpolation in a 2x2 environment), or <b>BICUBIC</b>
    #    (cubic spline interpolation in a 4x4 environment).
    #    If omitted, or if the image has mode "1" or "P", it is
    #    set <b>NEAREST</b>.
    # @param expand Optional expansion flag.  If true, expands the output
    #    image to make it large enough to hold the entire rotated image.
    #    If false or omitted, make the output image the same size as the
    #    input image.
    # @return An Image object.

    def rotate(self, angle, resample=NEAREST, expand=0):
        "Rotate image.  Angle given as degrees counter-clockwise."

        if expand:
            import math
            angle = -angle * math.pi / 180
            matrix = [
                 math.cos(angle), math.sin(angle), 0.0,
                -math.sin(angle), math.cos(angle), 0.0
                 ]
            def transform(x, y, (a, b, c, d, e, f)=matrix):
                return a*x + b*y + c, d*x + e*y + f

            # calculate output size
            w, h = self.size
            xx = []
            yy = []
            for x, y in ((0, 0), (w, 0), (w, h), (0, h)):
                x, y = transform(x, y)
                xx.append(x)
                yy.append(y)
            w = int(math.ceil(max(xx)) - math.floor(min(xx)))
            h = int(math.ceil(max(yy)) - math.floor(min(yy)))

            # adjust center
            x, y = transform(w / 2.0, h / 2.0)
            matrix[2] = self.size[0] / 2.0 - x
            matrix[5] = self.size[1] / 2.0 - y

            return self.transform((w, h), AFFINE, matrix, resample)

        if resample not in (NEAREST, BILINEAR, BICUBIC):
            raise ValueError("unknown resampling filter")

        self.load()

        if self.mode in ("1", "P"):
            resample = NEAREST

        return self._new(self.im.rotate(angle, resample))

    ##
    # Saves this image under the given filename.  If no format is
    # specified, the format to use is determined from the filename
    # extension, if possible.
    # <p>
    # Keyword options can be used to provide additional instructions
    # to the writer. If a writer doesn't recognise an option, it is
    # silently ignored. The available options are described later in
    # this handbook.
    # <p>
    # You can use a file object instead of a filename. In this case,
    # you must always specify the format. The file object must
    # implement the <b>seek</b>, <b>tell</b>, and <b>write</b>
    # methods, and be opened in binary mode.
    #
    # @def save(file, format=None, **options)
    # @param file File name or file object.
    # @param format Optional format override.  If omitted, the
    #    format to use is determined from the filename extension.
    #    If a file object was used instead of a filename, this
    #    parameter should always be used.
    # @param **options Extra parameters to the image writer.
    # @return None
    # @exception KeyError If the output format could not be determined
    #    from the file name.  Use the format option to solve this.
    # @exception IOError If the file could not be written.  The file
    #    may have been created, and may contain partial data.

    def save(self, fp, format=None, **params):
        "Save image to file or stream"

        if isStringType(fp):
            filename = fp
        else:
            if hasattr(fp, "name") and isStringType(fp.name):
                filename = fp.name
            else:
                filename = ""

        # may mutate self!
        self.load()

        self.encoderinfo = params
        self.encoderconfig = ()

        preinit()

        ext = string.lower(os.path.splitext(filename)[1])

        if not format:
            try:
                format = EXTENSION[ext]
            except KeyError:
                init()
                try:
                    format = EXTENSION[ext]
                except KeyError:
                    raise KeyError(ext) # unknown extension

        try:
            save_handler = SAVE[string.upper(format)]
        except KeyError:
            init()
            save_handler = SAVE[string.upper(format)] # unknown format

        if isStringType(fp):
            import __builtin__
            fp = __builtin__.open(fp, "wb")
            close = 1
        else:
            close = 0

        try:
            save_handler(self, fp, filename)
        finally:
            # do what we can to clean up
            if close:
                fp.close()

    ##
    # Seeks to the given frame in this sequence file. If you seek
    # beyond the end of the sequence, the method raises an
    # <b>EOFError</b> exception. When a sequence file is opened, the
    # library automatically seeks to frame 0.
    # <p>
    # Note that in the current version of the library, most sequence
    # formats only allows you to seek to the next frame.
    #
    # @param frame Frame number, starting at 0.
    # @exception EOFError If the call attempts to seek beyond the end
    #     of the sequence.
    # @see #Image.tell

    def seek(self, frame):
        "Seek to given frame in sequence file"

        # overridden by file handlers
        if frame != 0:
            raise EOFError

    ##
    # Displays this image. This method is mainly intended for
    # debugging purposes.
    # <p>
    # On Unix platforms, this method saves the image to a temporary
    # PPM file, and calls the <b>xv</b> utility.
    # <p>
    # On Windows, it saves the image to a temporary BMP file, and uses
    # the standard BMP display utility to show it (usually Paint).
    #
    # @def show(title=None)
    # @param title Optional title to use for the image window,
    #    where possible.

    def show(self, title=None, command=None):
        "Display image (for debug purposes only)"

        _show(self, title=title, command=command)

    ##
    # Split this image into individual bands. This method returns a
    # tuple of individual image bands from an image. For example,
    # splitting an "RGB" image creates three new images each
    # containing a copy of one of the original bands (red, green,
    # blue).
    #
    # @return A tuple containing bands.

    def split(self):
        "Split image into bands"

        if self.im.bands == 1:
            ims = [self.copy()]
        else:
            ims = []
            self.load()
            for i in range(self.im.bands):
                ims.append(self._new(self.im.getband(i)))
        return tuple(ims)

    ##
    # Returns the current frame number.
    #
    # @return Frame number, starting with 0.
    # @see #Image.seek

    def tell(self):
        "Return current frame number"

        return 0

    ##
    # Make this image into a thumbnail.  This method modifies the
    # image to contain a thumbnail version of itself, no larger than
    # the given size.  This method calculates an appropriate thumbnail
    # size to preserve the aspect of the image, calls the {@link
    # #Image.draft} method to configure the file reader (where
    # applicable), and finally resizes the image.
    # <p>
    # Note that the bilinear and bicubic filters in the current
    # version of PIL are not well-suited for thumbnail generation.
    # You should use <b>ANTIALIAS</b> unless speed is much more
    # important than quality.
    # <p>
    # Also note that this function modifies the Image object in place.
    # If you need to use the full resolution image as well, apply this
    # method to a {@link #Image.copy} of the original image.
    #
    # @param size Requested size.
    # @param resample Optional resampling filter.  This can be one
    #    of <b>NEAREST</b>, <b>BILINEAR</b>, <b>BICUBIC</b>, or
    #    <b>ANTIALIAS</b> (best quality).  If omitted, it defaults
    #    to <b>NEAREST</b> (this will be changed to ANTIALIAS in a
    #    future version).
    # @return None

    def thumbnail(self, size, resample=NEAREST):
        "Create thumbnail representation (modifies image in place)"

        # FIXME: the default resampling filter will be changed
        # to ANTIALIAS in future versions

        # preserve aspect ratio
        x, y = self.size
        if x > size[0]: y = int(max(y * size[0] / x, 1)); x = int(size[0])
        if y > size[1]: x = int(max(x * size[1] / y, 1)); y = int(size[1])
        size = x, y

        if size == self.size:
            return

        self.draft(None, size)

        self.load()

        try:
            im = self.resize(size, resample)
        except ValueError:
            if resample != ANTIALIAS:
                raise
            im = self.resize(size, NEAREST) # fallback

        self.im = im.im
        self.mode = im.mode
        self.size = size

        self.readonly = 0

    # FIXME: the different tranform methods need further explanation
    # instead of bloating the method docs, add a separate chapter.

    ##
    # Transforms this image.  This method creates a new image with the
    # given size, and the same mode as the original, and copies data
    # to the new image using the given transform.
    # <p>
    # @def transform(size, method, data, resample=NEAREST)
    # @param size The output size.
    # @param method The transformation method.  This is one of
    #   <b>EXTENT</b> (cut out a rectangular subregion), <b>AFFINE</b>
    #   (affine transform), <b>PERSPECTIVE</b> (perspective
    #   transform), <b>QUAD</b> (map a quadrilateral to a
    #   rectangle), or <b>MESH</b> (map a number of source quadrilaterals
    #   in one operation).
    # @param data Extra data to the transformation method.
    # @param resample Optional resampling filter.  It can be one of
    #    <b>NEAREST</b> (use nearest neighbour), <b>BILINEAR</b>
    #    (linear interpolation in a 2x2 environment), or
    #    <b>BICUBIC</b> (cubic spline interpolation in a 4x4
    #    environment). If omitted, or if the image has mode
    #    "1" or "P", it is set to <b>NEAREST</b>.
    # @return An Image object.

    def transform(self, size, method, data=None, resample=NEAREST, fill=1):
        "Transform image"

        if isinstance(method, ImageTransformHandler):
            return method.transform(size, self, resample=resample, fill=fill)
        if hasattr(method, "getdata"):
            # compatibility w. old-style transform objects
            method, data = method.getdata()
        if data is None:
            raise ValueError("missing method data")
        im = new(self.mode, size, None)
        if method == MESH:
            # list of quads
            for box, quad in data:
                im.__transformer(box, self, QUAD, quad, resample, fill)
        else:
            im.__transformer((0, 0)+size, self, method, data, resample, fill)

        return im

    def __transformer(self, box, image, method, data,
                      resample=NEAREST, fill=1):

        # FIXME: this should be turned into a lazy operation (?)

        w = box[2]-box[0]
        h = box[3]-box[1]

        if method == AFFINE:
            # change argument order to match implementation
            data = (data[2], data[0], data[1],
                    data[5], data[3], data[4])
        elif method == EXTENT:
            # convert extent to an affine transform
            x0, y0, x1, y1 = data
            xs = float(x1 - x0) / w
            ys = float(y1 - y0) / h
            method = AFFINE
            data = (x0 + xs/2, xs, 0, y0 + ys/2, 0, ys)
        elif method == PERSPECTIVE:
            # change argument order to match implementation
            data = (data[2], data[0], data[1],
                    data[5], data[3], data[4],
                    data[6], data[7])
        elif method == QUAD:
            # quadrilateral warp.  data specifies the four corners
            # given as NW, SW, SE, and NE.
            nw = data[0:2]; sw = data[2:4]; se = data[4:6]; ne = data[6:8]
            x0, y0 = nw; As = 1.0 / w; At = 1.0 / h
            data = (x0, (ne[0]-x0)*As, (sw[0]-x0)*At,
                    (se[0]-sw[0]-ne[0]+x0)*As*At,
                    y0, (ne[1]-y0)*As, (sw[1]-y0)*At,
                    (se[1]-sw[1]-ne[1]+y0)*As*At)
        else:
            raise ValueError("unknown transformation method")

        if resample not in (NEAREST, BILINEAR, BICUBIC):
            raise ValueError("unknown resampling filter")

        image.load()

        self.load()

        if image.mode in ("1", "P"):
            resample = NEAREST

        self.im.transform2(box, image.im, method, data, resample, fill)

    ##
    # Returns a flipped or rotated copy of this image.
    #
    # @param method One of <b>FLIP_LEFT_RIGHT</b>, <b>FLIP_TOP_BOTTOM</b>,
    # <b>ROTATE_90</b>, <b>ROTATE_180</b>, or <b>ROTATE_270</b>.

    def transpose(self, method):
        "Transpose image (flip or rotate in 90 degree steps)"

        self.load()
        im = self.im.transpose(method)
        return self._new(im)

# --------------------------------------------------------------------
# Lazy operations

class _ImageCrop(Image):

    def __init__(self, im, box):

        Image.__init__(self)

        x0, y0, x1, y1 = box
        if x1 < x0:
            x1 = x0
        if y1 < y0:
            y1 = y0

        self.mode = im.mode
        self.size = x1-x0, y1-y0

        self.__crop = x0, y0, x1, y1

        self.im = im.im

    def load(self):

        # lazy evaluation!
        if self.__crop:
            self.im = self.im.crop(self.__crop)
            self.__crop = None

        if self.im:
            return self.im.pixel_access(self.readonly)

        # FIXME: future versions should optimize crop/paste
        # sequences!

# --------------------------------------------------------------------
# Abstract handlers.

class ImagePointHandler:
    # used as a mixin by point transforms (for use with im.point)
    pass

class ImageTransformHandler:
    # used as a mixin by geometry transforms (for use with im.transform)
    pass

# --------------------------------------------------------------------
# Factories

#
# Debugging

def _wedge():
    "Create greyscale wedge (for debugging only)"

    return Image()._new(core.wedge("L"))

##
# Creates a new image with the given mode and size.
#
# @param mode The mode to use for the new image.
# @param size A 2-tuple, containing (width, height) in pixels.
# @param color What colour to use for the image.  Default is black.
#    If given, this should be a single integer or floating point value
#    for single-band modes, and a tuple for multi-band modes (one value
#    per band).  When creating RGB images, you can also use colour
#    strings as supported by the ImageColor module.  If the colour is
#    None, the image is not initialised.
# @return An Image object.

def new(mode, size, color=0):
    "Create a new image"

    if color is None:
        # don't initialize
        return Image()._new(core.new(mode, size))

    if isStringType(color):
        # css3-style specifier

        import ImageColor
        color = ImageColor.getcolor(color, mode)

    return Image()._new(core.fill(mode, size, color))

##
# Creates an image memory from pixel data in a string.
# <p>
# In its simplest form, this function takes three arguments
# (mode, size, and unpacked pixel data).
# <p>
# You can also use any pixel decoder supported by PIL.  For more
# information on available decoders, see the section <a
# href="pil-decoder.htm"><i>Writing Your Own File Decoder</i></a>.
# <p>
# Note that this function decodes pixel data only, not entire images.
# If you have an entire image in a string, wrap it in a
# <b>StringIO</b> object, and use {@link #open} to load it.
#
# @param mode The image mode.
# @param size The image size.
# @param data An 8-bit string containing raw data for the given mode.
# @param decoder_name What decoder to use.
# @param *args Additional parameters for the given decoder.
# @return An Image object.

def fromstring(mode, size, data, decoder_name="raw", *args):
    "Load image from string"

    # may pass tuple instead of argument list
    if len(args) == 1 and isTupleType(args[0]):
        args = args[0]

    if decoder_name == "raw" and args == ():
        args = mode

    im = new(mode, size)
    im.fromstring(data, decoder_name, args)
    return im

##
# (New in 1.1.4) Creates an image memory from pixel data in a string
# or byte buffer.
# <p>
# This function is similar to {@link #fromstring}, but uses data in
# the byte buffer, where possible.  This means that changes to the
# original buffer object are reflected in this image).  Not all modes
# can share memory; supported modes include "L", "RGBX", "RGBA", and
# "CMYK".
# <p>
# Note that this function decodes pixel data only, not entire images.
# If you have an entire image file in a string, wrap it in a
# <b>StringIO</b> object, and use {@link #open} to load it.
# <p>
# In the current version, the default parameters used for the "raw"
# decoder differs from that used for {@link fromstring}.  This is a
# bug, and will probably be fixed in a future release.  The current
# release issues a warning if you do this; to disable the warning,
# you should provide the full set of parameters.  See below for
# details.
#
# @param mode The image mode.
# @param size The image size.
# @param data An 8-bit string or other buffer object containing raw
#     data for the given mode.
# @param decoder_name What decoder to use.
# @param *args Additional parameters for the given decoder.  For the
#     default encoder ("raw"), it's recommended that you provide the
#     full set of parameters:
#     <b>frombuffer(mode, size, data, "raw", mode, 0, 1)</b>.
# @return An Image object.
# @since 1.1.4

def frombuffer(mode, size, data, decoder_name="raw", *args):
    "Load image from string or buffer"

    # may pass tuple instead of argument list
    if len(args) == 1 and isTupleType(args[0]):
        args = args[0]

    if decoder_name == "raw":
        if args == ():
            if warnings:
                warnings.warn(
                    "the frombuffer defaults may change in a future release; "
                    "for portability, change the call to read:\n"
                    "  frombuffer(mode, size, data, 'raw', mode, 0, 1)",
                    RuntimeWarning, stacklevel=2
                )
            args = mode, 0, -1 # may change to (mode, 0, 1) post-1.1.6
        if args[0] in _MAPMODES:
            im = new(mode, (1,1))
            im = im._new(
                core.map_buffer(data, size, decoder_name, None, 0, args)
                )
            im.readonly = 1
            return im

    return fromstring(mode, size, data, decoder_name, args)


##
# (New in 1.1.6) Creates an image memory from an object exporting
# the array interface (using the buffer protocol).
#
# If obj is not contiguous, then the tostring method is called
# and {@link frombuffer} is used.
#
# @param obj Object with array interface
# @param mode Mode to use (will be determined from type if None)
# @return An image memory.

def fromarray(obj, mode=None):
    arr = obj.__array_interface__
    shape = arr['shape']
    ndim = len(shape)
    try:
        strides = arr['strides']
    except KeyError:
        strides = None
    if mode is None:
        try:
            typekey = (1, 1) + shape[2:], arr['typestr']
            mode, rawmode = _fromarray_typemap[typekey]
        except KeyError:
            # print typekey
            raise TypeError("Cannot handle this data type")
    else:
        rawmode = mode
    if mode in ["1", "L", "I", "P", "F"]:
        ndmax = 2
    elif mode == "RGB":
        ndmax = 3
    else:
        ndmax = 4
    if ndim > ndmax:
        raise ValueError("Too many dimensions.")

    size = shape[1], shape[0]
    if strides is not None:
        obj = obj.tostring()

    return frombuffer(mode, size, obj, "raw", rawmode, 0, 1)

_fromarray_typemap = {
    # (shape, typestr) => mode, rawmode
    # first two members of shape are set to one
    # ((1, 1), "|b1"): ("1", "1"), # broken
    ((1, 1), "|u1"): ("L", "L"),
    ((1, 1), "|i1"): ("I", "I;8"),
    ((1, 1), "<i2"): ("I", "I;16"),
    ((1, 1), ">i2"): ("I", "I;16B"),
    ((1, 1), "<i4"): ("I", "I;32"),
    ((1, 1), ">i4"): ("I", "I;32B"),
    ((1, 1), "<f4"): ("F", "F;32F"),
    ((1, 1), ">f4"): ("F", "F;32BF"),
    ((1, 1), "<f8"): ("F", "F;64F"),
    ((1, 1), ">f8"): ("F", "F;64BF"),
    ((1, 1, 3), "|u1"): ("RGB", "RGB"),
    ((1, 1, 4), "|u1"): ("RGBA", "RGBA"),
    }

# shortcuts
_fromarray_typemap[((1, 1), _ENDIAN + "i4")] = ("I", "I")
_fromarray_typemap[((1, 1), _ENDIAN + "f4")] = ("F", "F")

##
# Opens and identifies the given image file.
# <p>
# This is a lazy operation; this function identifies the file, but the
# actual image data is not read from the file until you try to process
# the data (or call the {@link #Image.load} method).
#
# @def open(file, mode="r")
# @param file A filename (string) or a file object.  The file object
#    must implement <b>read</b>, <b>seek</b>, and <b>tell</b> methods,
#    and be opened in binary mode.
# @param mode The mode.  If given, this argument must be "r".
# @return An Image object.
# @exception IOError If the file cannot be found, or the image cannot be
#    opened and identified.
# @see #new

def open(fp, mode="r"):
    "Open an image file, without loading the raster data"

    if mode != "r":
        raise ValueError("bad mode")

    if isStringType(fp):
        import __builtin__
        filename = fp
        fp = __builtin__.open(fp, "rb")
    else:
        filename = ""

    prefix = fp.read(16)

    preinit()

    for i in ID:
        try:
            factory, accept = OPEN[i]
            if not accept or accept(prefix):
                fp.seek(0)
                return factory(fp, filename)
        except (SyntaxError, IndexError, TypeError):
            pass

    if init():

        for i in ID:
            try:
                factory, accept = OPEN[i]
                if not accept or accept(prefix):
                    fp.seek(0)
                    return factory(fp, filename)
            except (SyntaxError, IndexError, TypeError):
                pass

    raise IOError("cannot identify image file")

#
# Image processing.

##
# Creates a new image by interpolating between two input images, using
# a constant alpha.
#
# <pre>
#    out = image1 * (1.0 - alpha) + image2 * alpha
# </pre>
#
# @param im1 The first image.
# @param im2 The second image.  Must have the same mode and size as
#    the first image.
# @param alpha The interpolation alpha factor.  If alpha is 0.0, a
#    copy of the first image is returned. If alpha is 1.0, a copy of
#    the second image is returned. There are no restrictions on the
#    alpha value. If necessary, the result is clipped to fit into
#    the allowed output range.
# @return An Image object.

def blend(im1, im2, alpha):
    "Interpolate between images."

    im1.load()
    im2.load()
    return im1._new(core.blend(im1.im, im2.im, alpha))

##
# Creates a new image by interpolating between two input images,
# using the mask as alpha.
#
# @param image1 The first image.
# @param image2 The second image.  Must have the same mode and
#    size as the first image.
# @param mask A mask image.  This image can can have mode
#    "1", "L", or "RGBA", and must have the same size as the
#    other two images.

def composite(image1, image2, mask):
    "Create composite image by blending images using a transparency mask"

    image = image2.copy()
    image.paste(image1, None, mask)
    return image

##
# Applies the function (which should take one argument) to each pixel
# in the given image. If the image has more than one band, the same
# function is applied to each band. Note that the function is
# evaluated once for each possible pixel value, so you cannot use
# random components or other generators.
#
# @def eval(image, function)
# @param image The input image.
# @param function A function object, taking one integer argument.
# @return An Image object.

def eval(image, *args):
    "Evaluate image expression"

    return image.point(args[0])

##
# Creates a new image from a number of single-band images.
#
# @param mode The mode to use for the output image.
# @param bands A sequence containing one single-band image for
#     each band in the output image.  All bands must have the
#     same size.
# @return An Image object.

def merge(mode, bands):
    "Merge a set of single band images into a new multiband image."

    if getmodebands(mode) != len(bands) or "*" in mode:
        raise ValueError("wrong number of bands")
    for im in bands[1:]:
        if im.mode != getmodetype(mode):
            raise ValueError("mode mismatch")
        if im.size != bands[0].size:
            raise ValueError("size mismatch")
    im = core.new(mode, bands[0].size)
    for i in range(getmodebands(mode)):
        bands[i].load()
        im.putband(bands[i].im, i)
    return bands[0]._new(im)

# --------------------------------------------------------------------
# Plugin registry

##
# Register an image file plugin.  This function should not be used
# in application code.
#
# @param id An image format identifier.
# @param factory An image file factory method.
# @param accept An optional function that can be used to quickly
#    reject images having another format.

def register_open(id, factory, accept=None):
    id = string.upper(id)
    ID.append(id)
    OPEN[id] = factory, accept

##
# Registers an image MIME type.  This function should not be used
# in application code.
#
# @param id An image format identifier.
# @param mimetype The image MIME type for this format.

def register_mime(id, mimetype):
    MIME[string.upper(id)] = mimetype

##
# Registers an image save function.  This function should not be
# used in application code.
#
# @param id An image format identifier.
# @param driver A function to save images in this format.

def register_save(id, driver):
    SAVE[string.upper(id)] = driver

##
# Registers an image extension.  This function should not be
# used in application code.
#
# @param id An image format identifier.
# @param extension An extension used for this format.

def register_extension(id, extension):
    EXTENSION[string.lower(extension)] = string.upper(id)


# --------------------------------------------------------------------
# Simple display support.  User code may override this.

def _show(image, **options):
    # override me, as necessary
    apply(_showxv, (image,), options)

def _showxv(image, title=None, **options):
    import ImageShow
    apply(ImageShow.show, (image, title), options)
