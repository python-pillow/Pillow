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

from PIL import Image


try:
    # built-in driver (1.1.3 and later)
    grabber = Image.core.grabscreen
except AttributeError:
    try:
        # stand-alone driver (pil plus)
        import _grabscreen
        grabber = _grabscreen.grab
    except ImportError:
        # allow the module to be imported by autodoc
        grabber = None


def grab(bbox=None):
    """
    Take a snapshot of the screen. The pixels inside the bounding box are
    returned as an "RGB" image. If the bounding box is omitted, the entire
    screen is copied.

    .. versionadded:: 1.1.3

    :param bbox: What region to copy. Default is the entire screen.
    :return: An image
    """
    size, data = grabber()
    im = Image.frombytes(
        "RGB", size, data,
        # RGB, 32-bit line padding, origo in lower left corner
        "raw", "BGR", (size[0]*3 + 3) & -4, -1
        )
    if bbox:
        im = im.crop(bbox)
    return im

##

def grabclipboard():
    """
    Take a snapshot of the clipboard image, if any.

    .. versionadded:: 1.1.4

    :return: An image, a list of filenames, or None if the clipboard does
             not contain image data or filenames.  Note that if a list is
             returned, the filenames may not represent image files.
    """
    debug = 0 # temporary interface
    data = Image.core.grabclipboard(debug)
    if isinstance(data, bytes):
        from PIL import BmpImagePlugin
        import io
        return BmpImagePlugin.DibImageFile(io.BytesIO(data))
    return data
