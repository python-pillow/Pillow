# minimal sanity check
from __future__ import print_function

import sys
import os

if "--installed" in sys.argv:
    sys_path_0 = sys.path[0]
    del sys.path[0]

from PIL import Image, ImageDraw, ImageFilter, ImageMath

if "--installed" in sys.argv:
    sys.path.insert(0, sys_path_0)

ROOT = "."

try:
    Image.core.ping
except ImportError as v:
    print("***", v)
    sys.exit()
except AttributeError:
    pass


def _info(im):
    im.load()
    return im.format, im.mode, im.size


def testimage():
    """
    PIL lets you create in-memory images with various pixel types:

    >>> im = Image.new("1", (128, 128)) # monochrome
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

    >>> im = Image.open(os.path.join(ROOT, "Images/lena.gif"))
    >>> _info(im)
    ('GIF', 'P', (128, 128))
    >>> _info(Image.open(os.path.join(ROOT, "Images/lena.ppm")))
    ('PPM', 'RGB', (128, 128))
    >>> try:
    ...  _info(Image.open(os.path.join(ROOT, "Images/lena.jpg")))
    ... except IOError as v:
    ...  print(v)
    ('JPEG', 'RGB', (128, 128))

    PIL doesn't actually load the image data until it's needed,
    or you call the "load" method:

    >>> im = Image.open(os.path.join(ROOT, "Images/lena.ppm"))
    >>> print(im.im) # internal image attribute
    None
    >>> a = im.load()
    >>> type(im.im) # doctest: +ELLIPSIS
    <... '...ImagingCore'>

    You can apply many different operations on images.  Most
    operations return a new image:

    >>> im = Image.open(os.path.join(ROOT, "Images/lena.ppm"))
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
    ((61, 255), (26, 234), (44, 223))
    >>> im.getpixel((0, 0))
    (223, 162, 133)
    >>> len(im.getprojection())
    2
    >>> len(im.histogram())
    768
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
    >>> _info(im.transform((512, 512), Image.AFFINE, (1,0,0,0,1,0)))
    (None, 'RGB', (512, 512))
    >>> _info(im.transform((512, 512), Image.EXTENT, (32,32,96,96)))
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

    >>> im = ImageMath.eval("float(im + 20)", im=im.convert("L"))
    >>> im.mode, im.size
    ('F', (128, 128))

    PIL can do many other things, but I'll leave that for another
    day.  If you're curious, check the handbook, available from:

        http://www.pythonware.com

    Cheers /F
    """


def check_module(feature, module):
    try:
        __import__(module)
    except ImportError:
        print("***", feature, "support not installed")
    else:
        print("---", feature, "support ok")


def check_codec(feature, codec):
    if codec + "_encoder" not in dir(Image.core):
        print("***", feature, "support not installed")
    else:
        print("---", feature, "support ok")


if __name__ == "__main__":
    # check build sanity

    exit_status = 0

    print("-"*68)
    print("Pillow", Image.PILLOW_VERSION, "TEST SUMMARY ")
    print("-"*68)
    print("Python modules loaded from", os.path.dirname(Image.__file__))
    print("Binary modules loaded from", os.path.dirname(Image.core.__file__))
    print("-"*68)
    check_module("PIL CORE", "PIL._imaging")
    check_module("TKINTER", "PIL._imagingtk")
    check_codec("JPEG", "jpeg")
    check_codec("JPEG 2000", "jpeg2k")
    check_codec("ZLIB (PNG/ZIP)", "zip")
    check_codec("LIBTIFF", "libtiff")
    check_module("FREETYPE2", "PIL._imagingft")
    check_module("LITTLECMS2", "PIL._imagingcms")
    check_module("WEBP", "PIL._webp")
    try:
        from PIL import _webp
        if _webp.WebPDecoderBuggyAlpha():
            print("***", "Transparent WEBP", "support not installed")
        else:
            print("---", "Transparent WEBP", "support ok")
    except Exception:
        pass
    print("-"*68)

    # use doctest to make sure the test program behaves as documented!
    import doctest
    import selftest
    print("Running selftest:")
    status = doctest.testmod(selftest)
    if status[0]:
        print("*** %s tests of %d failed." % status)
        exit_status = 1
    else:
        print("--- %s tests passed." % status[1])

    sys.exit(exit_status)
