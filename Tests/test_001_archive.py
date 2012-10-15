import PIL
import PIL.Image

import glob, os

for file in glob.glob("../pil-archive/*"):
    f, e = os.path.splitext(file)
    if e in [".txt", ".ttf", ".otf", ".zip"]:
        continue
    try:
        im = PIL.Image.open(file)
        im.load()
    except IOError as v:
        print("-", "failed to open", file, "-", v)
    else:
        print("+", file, im.mode, im.size, im.format)
        if e == ".exif":
            try:
                info = im._getexif()
            except KeyError as v:
                print("-", "failed to get exif info from", file, "-", v)

print("ok")
