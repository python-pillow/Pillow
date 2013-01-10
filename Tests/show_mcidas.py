import sys
sys.path.insert(0, ".")

from PIL import Image
from PIL import ImageMath

try:
    filename = sys.argv[1]
except IndexError:
    filename = "../pil-archive/goes12.2005.140.190925.BAND_01.mcidas"
    # filename = "../pil-archive/goes12.2005.140.190925.BAND_01.im"

im = Image.open(filename)

print(im.format)
print(im.mode)
print(im.size)
print(im.tile)

lo, hi = im.getextrema()

print("map", lo, hi, "->", end=' ')
im = ImageMath.eval("convert(im*255/hi, 'L')", im=im, hi=hi)
print(im.getextrema())

im.show()
