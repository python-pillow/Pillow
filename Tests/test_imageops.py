from tester import *

from PIL import Image
from PIL import ImageOps

class Deformer:
    def getmesh(self, im):
        x, y = im.size
        return [((0, 0, x, y), (0, 0, x, 0, x, y, y, 0))]

deformer = Deformer()

def test_sanity():

    ImageOps.autocontrast(lena("L"))
    ImageOps.autocontrast(lena("RGB"))

    ImageOps.autocontrast(lena("L"), cutoff=10)
    ImageOps.autocontrast(lena("L"), ignore=[0, 255])

    ImageOps.colorize(lena("L"), (0, 0, 0), (255, 255, 255))
    ImageOps.colorize(lena("L"), "black", "white")

    ImageOps.crop(lena("L"), 1)
    ImageOps.crop(lena("RGB"), 1)

    ImageOps.deform(lena("L"), deformer)
    ImageOps.deform(lena("RGB"), deformer)

    ImageOps.equalize(lena("L"))
    ImageOps.equalize(lena("RGB"))

    ImageOps.expand(lena("L"), 1)
    ImageOps.expand(lena("RGB"), 1)
    ImageOps.expand(lena("L"), 2, "blue")
    ImageOps.expand(lena("RGB"), 2, "blue")

    ImageOps.fit(lena("L"), (128, 128))
    ImageOps.fit(lena("RGB"), (128, 128))

    ImageOps.flip(lena("L"))
    ImageOps.flip(lena("RGB"))

    ImageOps.grayscale(lena("L"))
    ImageOps.grayscale(lena("RGB"))

    ImageOps.invert(lena("L"))
    ImageOps.invert(lena("RGB"))

    ImageOps.mirror(lena("L"))
    ImageOps.mirror(lena("RGB"))

    ImageOps.posterize(lena("L"), 4)
    ImageOps.posterize(lena("RGB"), 4)

    ImageOps.solarize(lena("L"))
    ImageOps.solarize(lena("RGB"))

    success()

def test_1pxfit():
    # Division by zero in equalize if image is 1 pixel high
    newimg = ImageOps.fit(lena("RGB").resize((1,1)), (35,35))
    assert_equal(newimg.size,(35,35))
    
    newimg = ImageOps.fit(lena("RGB").resize((1,100)), (35,35))
    assert_equal(newimg.size,(35,35))

    newimg = ImageOps.fit(lena("RGB").resize((100,1)), (35,35))
    assert_equal(newimg.size,(35,35))

def test_pil163():
    # Division by zero in equalize if < 255 pixels in image (@PIL163)

    i = lena("RGB").resize((15, 16))

    ImageOps.equalize(i.convert("L"))
    ImageOps.equalize(i.convert("P"))
    ImageOps.equalize(i.convert("RGB"))

    success()
