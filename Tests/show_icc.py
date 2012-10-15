import sys
sys.path.insert(0, ".")

from PIL import Image
from PIL import ImageCms

try:
    filename = sys.argv[1]
except IndexError:
    filename = "../pil-archive/cmyk.jpg"

i = Image.open(filename)

print(i.format)
print(i.mode)
print(i.size)
print(i.tile)

p = ImageCms.getMemoryProfile(i.info["icc_profile"])

print(repr(p.product_name))
print(repr(p.product_info))

o = ImageCms.createProfile("sRGB")
t = ImageCms.buildTransformFromOpenProfiles(p, o, i.mode, "RGB")
i = ImageCms.applyTransform(i, t)

i.show()
