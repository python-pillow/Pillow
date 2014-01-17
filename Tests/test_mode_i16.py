from tester import *

from PIL import Image

def verify(im1):
    im2 = lena("I")
    assert_equal(im1.size, im2.size)
    pix1 = im1.load()
    pix2 = im2.load()
    for y in range(im1.size[1]):
        for x in range(im1.size[0]):
            xy = x, y
            if pix1[xy] != pix2[xy]:
                failure(
                    "got %r from mode %s at %s, expected %r" %
                    (pix1[xy], im1.mode, xy, pix2[xy])
                    )
                return
    success()

def test_basic():
    # PIL 1.1 has limited support for 16-bit image data.  Check that
    # create/copy/transform and save works as expected.

    def basic(mode):

        imIn = lena("I").convert(mode)
        verify(imIn)

        w, h = imIn.size

        imOut = imIn.copy()
        verify(imOut) # copy

        imOut = imIn.transform((w, h), Image.EXTENT, (0, 0, w, h))
        verify(imOut) # transform

        filename = tempfile("temp.im")
        imIn.save(filename)

        imOut = Image.open(filename)

        verify(imIn)
        verify(imOut)

        imOut = imIn.crop((0, 0, w, h))
        verify(imOut)

        imOut = Image.new(mode, (w, h), None)
        imOut.paste(imIn.crop((0, 0, w//2, h)), (0, 0))
        imOut.paste(imIn.crop((w//2, 0, w, h)), (w//2, 0))

        verify(imIn)
        verify(imOut)

        imIn = Image.new(mode, (1, 1), 1)
        assert_equal(imIn.getpixel((0, 0)), 1)

        imIn.putpixel((0, 0), 2)
        assert_equal(imIn.getpixel((0, 0)), 2)

        if mode == "L":
            max = 255
        else:
            max = 32767

        imIn = Image.new(mode, (1, 1), 256)
        assert_equal(imIn.getpixel((0, 0)), min(256, max))

        imIn.putpixel((0, 0), 512)
        assert_equal(imIn.getpixel((0, 0)), min(512, max))

    basic("L")

    basic("I;16")
    basic("I;16B")
    basic("I;16L")

    basic("I")


def test_tobytes():

    def tobytes(mode):
        return Image.new(mode, (1, 1), 1).tobytes()

    order = 1 if Image._ENDIAN == '<' else -1

    assert_equal(tobytes("L"), b"\x01")
    assert_equal(tobytes("I;16"), b"\x01\x00")
    assert_equal(tobytes("I;16B"), b"\x00\x01")
    assert_equal(tobytes("I"), b"\x01\x00\x00\x00"[::order])


def test_convert():

    im = lena("I")

    verify(im.convert("I;16"))
    verify(im.convert("I;16").convert("L"))
    verify(im.convert("I;16").convert("I"))

    verify(im.convert("I;16B"))
    verify(im.convert("I;16B").convert("L"))
    verify(im.convert("I;16B").convert("I"))
