#!/usr/bin/env python3
# minimal sanity check
from __future__ import annotations

import sys

from PIL import Image, features

try:
    Image.core.ping
except ImportError as v:
    print("***", v)
    sys.exit()
except AttributeError:
    pass


def testimage() -> None:
    """
    PIL lets you create in-memory images with various pixel types:

    >>> from PIL import Image, ImageDraw, ImageFilter, ImageMath
    >>> im = Image.new("1", (128, 128)) # monochrome
    >>> def _info(im): return im.format, im.mode, im.size
    >>> _info(im)
    (None, '1', (128, 128))
    >>> _info(Image.new("L", (128, 128))) # grayscale (luminance)
    (None, 'L', (128, 128))
    >>> _info(Image.new("P", (128, 128))) # palette
    (None, 'P', (128, 128))
    >>> _info(Image.new("RGB", (128, 128))) # truecolor
    (None, 'RGB', (128, 128))
    >>> _info(Image.new("I", (128, 128))) # 32-bit integer
    (None, 'I', (128, 128))
    >>> _info(Image.new("F", (128, 128))) # 32-bit floating point
    (None, 'F', (128, 128))

    Or open existing files:

    >>> with Image.open("Tests/images/hopper.gif") as im:
    ...     _info(im)
    ('GIF', 'P', (128, 128))
    >>> _info(Image.open("Tests/images/hopper.ppm"))
    ('PPM', 'RGB', (128, 128))
    >>> try:
    ...  _info(Image.open("Tests/images/hopper.jpg"))
    ... except OSError as v:
    ...  print(v)
    ('JPEG', 'RGB', (128, 128))

    PIL doesn't actually load the image data until it's needed,
    or you call the "load" method:

    >>> im = Image.open("Tests/images/hopper.ppm")
    >>> print(im._im) # internal image attribute
    None
    >>> a = im.load()
    >>> type(im.im) # doctest: +ELLIPSIS
    <... '...ImagingCore'>

    You can apply many different operations on images.  Most
    operations return a new image:

    >>> im = Image.open("Tests/images/hopper.ppm")
    >>> _info(im.convert("L"))
    (None, 'L', (128, 128))
    >>> _info(im.copy())
    (None, 'RGB', (128, 128))
    >>> _info(im.crop((32, 32, 96, 96)))
    (None, 'RGB', (64, 64))
    >>> _info(im.filter(ImageFilter.BLUR))
    (None, 'RGB', (128, 128))
    >>> im.getbands()
    ('R', 'G', 'B')
    >>> im.getbbox()
    (0, 0, 128, 128)
    >>> len(im.getdata())
    16384
    >>> im.getextrema()
    ((0, 255), (0, 255), (0, 255))
    >>> im.getpixel((0, 0))
    (20, 20, 70)
    >>> len(im.getprojection())
    2
    >>> len(im.histogram())
    768
    >>> '%.7f' % im.entropy()
    '8.8212866'
    >>> _info(im.point(list(range(256))*3))
    (None, 'RGB', (128, 128))
    >>> _info(im.resize((64, 64)))
    (None, 'RGB', (64, 64))
    >>> _info(im.rotate(45))
    (None, 'RGB', (128, 128))
    >>> [_info(ch) for ch in im.split()]
    [(None, 'L', (128, 128)), (None, 'L', (128, 128)), (None, 'L', (128, 128))]
    >>> len(im.convert("1").tobitmap())
    10456
    >>> len(im.tobytes())
    49152
    >>> _info(im.transform((512, 512), Image.Transform.AFFINE, (1,0,0,0,1,0)))
    (None, 'RGB', (512, 512))
    >>> _info(im.transform((512, 512), Image.Transform.EXTENT, (32,32,96,96)))
    (None, 'RGB', (512, 512))

    The ImageDraw module lets you draw stuff in raster images:

    >>> im = Image.new("L", (128, 128), 64)
    >>> d = ImageDraw.ImageDraw(im)
    >>> d.line((0, 0, 128, 128), fill=128)
    >>> d.line((0, 128, 128, 0), fill=128)
    >>> im.getextrema()
    (64, 128)

    In 1.1.4, you can specify colors in a number of ways:

    >>> xy = 0, 0, 128, 128
    >>> im = Image.new("RGB", (128, 128), 0)
    >>> d = ImageDraw.ImageDraw(im)
    >>> d.rectangle(xy, "#f00")
    >>> im.getpixel((0, 0))
    (255, 0, 0)
    >>> d.rectangle(xy, "#ff0000")
    >>> im.getpixel((0, 0))
    (255, 0, 0)
    >>> d.rectangle(xy, "rgb(255,0,0)")
    >>> im.getpixel((0, 0))
    (255, 0, 0)
    >>> d.rectangle(xy, "rgb(100%,0%,0%)")
    >>> im.getpixel((0, 0))
    (255, 0, 0)
    >>> d.rectangle(xy, "hsl(0, 100%, 50%)")
    >>> im.getpixel((0, 0))
    (255, 0, 0)
    >>> d.rectangle(xy, "red")
    >>> im.getpixel((0, 0))
    (255, 0, 0)

    In 1.1.6, you can use the ImageMath module to do image
    calculations.

    >>> im = ImageMath.lambda_eval( \
      lambda args: args["float"](args["im"] + 20), im=im.convert("L") \
    )
    >>> im.mode, im.size
    ('F', (128, 128))

    PIL can do many other things, but I'll leave that for another
    day.

    Cheers /F
    """


if __name__ == "__main__":
    # check build sanity

    exit_status = 0

    features.pilinfo(sys.stdout, False)

    # use doctest to make sure the test program behaves as documented!
    import doctest

    print("Running selftest:")
    status = doctest.testmod(sys.modules[__name__])
    if status[0]:
        print(f"*** {status[0]} tests of {status[1]} failed.")
        exit_status = 1
    else:
        print(f"--- {status[1]} tests passed.")

    sys.exit(exit_status)
