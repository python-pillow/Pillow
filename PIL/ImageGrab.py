#
# The Python Imaging Library
# $Id$
#
# screen grabber (windows only)
#
# History:
# 2001-04-26 fl  created
# 2001-09-17 fl  use builtin driver, if present
# 2002-11-19 fl  added grabclipboard support
#
# Copyright (c) 2001-2002 by Secret Labs AB
# Copyright (c) 2001-2002 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import Image

##
# (New in 1.1.3)  The <b>ImageGrab</b> module can be used to copy
# the contents of the screen to a PIL image memory.
# <p>
# The current version works on Windows only.</p>
#
# @since 1.1.3
##

try:
    # built-in driver (1.1.3 and later)
    grabber = Image.core.grabscreen
except AttributeError:
    # stand-alone driver (pil plus)
    import _grabscreen
    grabber = _grabscreen.grab

##
# (New in 1.1.3) Take a snapshot of the screen.  The pixels inside the
# bounding box are returned as an "RGB" image.  If the bounding box is
# omitted, the entire screen is copied.
#
# @param bbox What region to copy.  Default is the entire screen.
# @return An image
# @since 1.1.3

def grab(bbox=None):
    size, data = grabber()
    im = Image.fromstring(
        "RGB", size, data,
        # RGB, 32-bit line padding, origo in lower left corner
        "raw", "BGR", (size[0]*3 + 3) & -4, -1
        )
    if bbox:
        im = im.crop(bbox)
    return im

##
# (New in 1.1.4) Take a snapshot of the clipboard image, if any.
#
# @return An image, a list of filenames, or None if the clipboard does
#     not contain image data or filenames.  Note that if a list is
#     returned, the filenames may not represent image files.
# @since 1.1.4

def grabclipboard():
    debug = 0 # temporary interface
    data = Image.core.grabclipboard(debug)
    if Image.isStringType(data):
        import BmpImagePlugin, StringIO
        return BmpImagePlugin.DibImageFile(StringIO.StringIO(data))
    return data
