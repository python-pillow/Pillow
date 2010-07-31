#
# The Python Imaging Library
# $Id$
#
# drawing interface operations
#
# History:
# 1996-04-13 fl   Created (experimental)
# 1996-08-07 fl   Filled polygons, ellipses.
# 1996-08-13 fl   Added text support
# 1998-06-28 fl   Handle I and F images
# 1998-12-29 fl   Added arc; use arc primitive to draw ellipses
# 1999-01-10 fl   Added shape stuff (experimental)
# 1999-02-06 fl   Added bitmap support
# 1999-02-11 fl   Changed all primitives to take options
# 1999-02-20 fl   Fixed backwards compatibility
# 2000-10-12 fl   Copy on write, when necessary
# 2001-02-18 fl   Use default ink for bitmap/text also in fill mode
# 2002-10-24 fl   Added support for CSS-style color strings
# 2002-12-10 fl   Added experimental support for RGBA-on-RGB drawing
# 2002-12-11 fl   Refactored low-level drawing API (work in progress)
# 2004-08-26 fl   Made Draw() a factory function, added getdraw() support
# 2004-09-04 fl   Added width support to line primitive
# 2004-09-10 fl   Added font mode handling
# 2006-06-19 fl   Added font bearing support (getmask2)
#
# Copyright (c) 1997-2006 by Secret Labs AB
# Copyright (c) 1996-2006 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import Image, ImageColor

try:
    import warnings
except ImportError:
    warnings = None

##
# A simple 2D drawing interface for PIL images.
# <p>
# Application code should use the <b>Draw</b> factory, instead of
# directly.

class ImageDraw:

    ##
    # Create a drawing instance.
    #
    # @param im The image to draw in.
    # @param mode Optional mode to use for color values.  For RGB
    #    images, this argument can be RGB or RGBA (to blend the
    #    drawing into the image).  For all other modes, this argument
    #    must be the same as the image mode.  If omitted, the mode
    #    defaults to the mode of the image.

    def __init__(self, im, mode=None):
        im.load()
        if im.readonly:
            im._copy() # make it writable
        blend = 0
        if mode is None:
            mode = im.mode
        if mode != im.mode:
            if mode == "RGBA" and im.mode == "RGB":
                blend = 1
            else:
                raise ValueError("mode mismatch")
        if mode == "P":
            self.palette = im.palette
        else:
            self.palette = None
        self.im = im.im
        self.draw = Image.core.draw(self.im, blend)
        self.mode = mode
        if mode in ("I", "F"):
            self.ink = self.draw.draw_ink(1, mode)
        else:
            self.ink = self.draw.draw_ink(-1, mode)
        if mode in ("1", "P", "I", "F"):
            # FIXME: fix Fill2 to properly support matte for I+F images
            self.fontmode = "1"
        else:
            self.fontmode = "L" # aliasing is okay for other modes
        self.fill = 0
        self.font = None

    ##
    # Set the default pen color.

    def setink(self, ink):
        # compatibility
        if warnings:
            warnings.warn(
                "'setink' is deprecated; use keyword arguments instead",
                DeprecationWarning, stacklevel=2
                )
        if Image.isStringType(ink):
            ink = ImageColor.getcolor(ink, self.mode)
        if self.palette and not Image.isNumberType(ink):
            ink = self.palette.getcolor(ink)
        self.ink = self.draw.draw_ink(ink, self.mode)

    ##
    # Set the default background color.

    def setfill(self, onoff):
        # compatibility
        if warnings:
            warnings.warn(
                "'setfill' is deprecated; use keyword arguments instead",
                DeprecationWarning, stacklevel=2
                )
        self.fill = onoff

    ##
    # Set the default font.

    def setfont(self, font):
        # compatibility
        self.font = font

    ##
    # Get the current default font.

    def getfont(self):
        if not self.font:
            # FIXME: should add a font repository
            import ImageFont
            self.font = ImageFont.load_default()
        return self.font

    def _getink(self, ink, fill=None):
        if ink is None and fill is None:
            if self.fill:
                fill = self.ink
            else:
                ink = self.ink
        else:
            if ink is not None:
                if Image.isStringType(ink):
                    ink = ImageColor.getcolor(ink, self.mode)
                if self.palette and not Image.isNumberType(ink):
                    ink = self.palette.getcolor(ink)
                ink = self.draw.draw_ink(ink, self.mode)
            if fill is not None:
                if Image.isStringType(fill):
                    fill = ImageColor.getcolor(fill, self.mode)
                if self.palette and not Image.isNumberType(fill):
                    fill = self.palette.getcolor(fill)
                fill = self.draw.draw_ink(fill, self.mode)
        return ink, fill

    ##
    # Draw an arc.

    def arc(self, xy, start, end, fill=None):
        ink, fill = self._getink(fill)
        if ink is not None:
            self.draw.draw_arc(xy, start, end, ink)

    ##
    # Draw a bitmap.

    def bitmap(self, xy, bitmap, fill=None):
        bitmap.load()
        ink, fill = self._getink(fill)
        if ink is None:
            ink = fill
        if ink is not None:
            self.draw.draw_bitmap(xy, bitmap.im, ink)

    ##
    # Draw a chord.

    def chord(self, xy, start, end, fill=None, outline=None):
        ink, fill = self._getink(outline, fill)
        if fill is not None:
            self.draw.draw_chord(xy, start, end, fill, 1)
        if ink is not None:
            self.draw.draw_chord(xy, start, end, ink, 0)

    ##
    # Draw an ellipse.

    def ellipse(self, xy, fill=None, outline=None):
        ink, fill = self._getink(outline, fill)
        if fill is not None:
            self.draw.draw_ellipse(xy, fill, 1)
        if ink is not None:
            self.draw.draw_ellipse(xy, ink, 0)

    ##
    # Draw a line, or a connected sequence of line segments.

    def line(self, xy, fill=None, width=0):
        ink, fill = self._getink(fill)
        if ink is not None:
            self.draw.draw_lines(xy, ink, width)

    ##
    # (Experimental) Draw a shape.

    def shape(self, shape, fill=None, outline=None):
        # experimental
        shape.close()
        ink, fill = self._getink(outline, fill)
        if fill is not None:
            self.draw.draw_outline(shape, fill, 1)
        if ink is not None:
            self.draw.draw_outline(shape, ink, 0)

    ##
    # Draw a pieslice.

    def pieslice(self, xy, start, end, fill=None, outline=None):
        ink, fill = self._getink(outline, fill)
        if fill is not None:
            self.draw.draw_pieslice(xy, start, end, fill, 1)
        if ink is not None:
            self.draw.draw_pieslice(xy, start, end, ink, 0)

    ##
    # Draw one or more individual pixels.

    def point(self, xy, fill=None):
        ink, fill = self._getink(fill)
        if ink is not None:
            self.draw.draw_points(xy, ink)

    ##
    # Draw a polygon.

    def polygon(self, xy, fill=None, outline=None):
        ink, fill = self._getink(outline, fill)
        if fill is not None:
            self.draw.draw_polygon(xy, fill, 1)
        if ink is not None:
            self.draw.draw_polygon(xy, ink, 0)

    ##
    # Draw a rectangle.

    def rectangle(self, xy, fill=None, outline=None):
        ink, fill = self._getink(outline, fill)
        if fill is not None:
            self.draw.draw_rectangle(xy, fill, 1)
        if ink is not None:
            self.draw.draw_rectangle(xy, ink, 0)

    ##
    # Draw text.

    def text(self, xy, text, fill=None, font=None, anchor=None):
        ink, fill = self._getink(fill)
        if font is None:
            font = self.getfont()
        if ink is None:
            ink = fill
        if ink is not None:
            try:
                mask, offset = font.getmask2(text, self.fontmode)
                xy = xy[0] + offset[0], xy[1] + offset[1]
            except AttributeError:
                try:
                    mask = font.getmask(text, self.fontmode)
                except TypeError:
                    mask = font.getmask(text)
            self.draw.draw_bitmap(xy, mask, ink)

    ##
    # Get the size of a given string, in pixels.

    def textsize(self, text, font=None):
        if font is None:
            font = self.getfont()
        return font.getsize(text)

##
# A simple 2D drawing interface for PIL images.
#
# @param im The image to draw in.
# @param mode Optional mode to use for color values.  For RGB
#    images, this argument can be RGB or RGBA (to blend the
#    drawing into the image).  For all other modes, this argument
#    must be the same as the image mode.  If omitted, the mode
#    defaults to the mode of the image.

def Draw(im, mode=None):
    try:
        return im.getdraw(mode)
    except AttributeError:
        return ImageDraw(im, mode)

# experimental access to the outline API
try:
    Outline = Image.core.outline
except:
    Outline = None

##
# (Experimental) A more advanced 2D drawing interface for PIL images,
# based on the WCK interface.
#
# @param im The image to draw in.
# @param hints An optional list of hints.
# @return A (drawing context, drawing resource factory) tuple.

def getdraw(im=None, hints=None):
    # FIXME: this needs more work!
    # FIXME: come up with a better 'hints' scheme.
    handler = None
    if not hints or "nicest" in hints:
        try:
            import _imagingagg
            handler = _imagingagg
        except ImportError:
            pass
    if handler is None:
        import ImageDraw2
        handler = ImageDraw2
    if im:
        im = handler.Draw(im)
    return im, handler

##
# (experimental) Fills a bounded region with a given color.
#
# @param image Target image.
# @param xy Seed position (a 2-item coordinate tuple).
# @param value Fill color.
# @param border Optional border value.  If given, the region consists of
#     pixels with a color different from the border color.  If not given,
#     the region consists of pixels having the same color as the seed
#     pixel.

def floodfill(image, xy, value, border=None):
    "Fill bounded region."
    # based on an implementation by Eric S. Raymond
    pixel = image.load()
    x, y = xy
    try:
        background = pixel[x, y]
        if background == value:
            return # seed point already has fill color
        pixel[x, y] = value
    except IndexError:
        return # seed point outside image
    edge = [(x, y)]
    if border is None:
        while edge:
            newedge = []
            for (x, y) in edge:
                for (s, t) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    try:
                        p = pixel[s, t]
                    except IndexError:
                        pass
                    else:
                        if p == background:
                            pixel[s, t] = value
                            newedge.append((s, t))
            edge = newedge
    else:
        while edge:
            newedge = []
            for (x, y) in edge:
                for (s, t) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    try:
                        p = pixel[s, t]
                    except IndexError:
                        pass
                    else:
                        if p != value and p != border:
                            pixel[s, t] = value
                            newedge.append((s, t))
            edge = newedge
