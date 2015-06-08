from __future__ import print_function
from PIL import Image


def version(module, version):
    v = getattr(module.core, version + "_version", None)
    if v:
        print(version, v)

version(Image, "jpeglib")
version(Image, "zlib")

try:
    from PIL import ImageFont
except ImportError:
    pass
else:
    version(ImageFont, "freetype2")

try:
    from PIL import ImageCms
except ImportError:
    pass
else:
    version(ImageCms, "littlecms")
