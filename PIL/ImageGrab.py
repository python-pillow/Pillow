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
    # stand-alone driver (pil plus)
    import _grabscreen
    grabber = _grabscreen.grab


def grab(bbox=None):
    size, data = grabber()
    im = Image.frombytes(
        "RGB", size, data,
        # RGB, 32-bit line padding, origo in lower left corner
        "raw", "BGR", (size[0]*3 + 3) & -4, -1
        )
    if bbox:
        im = im.crop(bbox)
    return im


def grabclipboard():
    debug = 0 # temporary interface
    data = Image.core.grabclipboard(debug)
    if isinstance(data, bytes):
        from PIL import BmpImagePlugin
        import io
        return BmpImagePlugin.DibImageFile(io.BytesIO(data))
    return data
