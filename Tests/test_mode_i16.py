from PIL import Image

from .helper import hopper

original = hopper().resize((32, 32)).convert("I")


def verify(im1):
    im2 = original.copy()
    assert im1.size == im2.size
    pix1 = im1.load()
    pix2 = im2.load()
    for y in range(im1.size[1]):
        for x in range(im1.size[0]):
            xy = x, y
            p1 = pix1[xy]
            p2 = pix2[xy]
            assert (
                p1 == p2
            ), f"got {repr(p1)} from mode {im1.mode} at {xy}, expected {repr(p2)}"


def test_basic(tmp_path):
    # PIL 1.1 has limited support for 16-bit image data.  Check that
    # create/copy/transform and save works as expected.

    def basic(mode):

        imIn = original.convert(mode)
        verify(imIn)

        w, h = imIn.size

        imOut = imIn.copy()
        verify(imOut)  # copy

        imOut = imIn.transform((w, h), Image.EXTENT, (0, 0, w, h))
        verify(imOut)  # transform

        filename = str(tmp_path / "temp.im")
        imIn.save(filename)

        with Image.open(filename) as imOut:

            verify(imIn)
            verify(imOut)

        imOut = imIn.crop((0, 0, w, h))
        verify(imOut)

        imOut = Image.new(mode, (w, h), None)
        imOut.paste(imIn.crop((0, 0, w // 2, h)), (0, 0))
        imOut.paste(imIn.crop((w // 2, 0, w, h)), (w // 2, 0))

        verify(imIn)
        verify(imOut)

        imIn = Image.new(mode, (1, 1), 1)
        assert imIn.getpixel((0, 0)) == 1

        imIn.putpixel((0, 0), 2)
        assert imIn.getpixel((0, 0)) == 2

        if mode == "L":
            maximum = 255
        else:
            maximum = 32767

        imIn = Image.new(mode, (1, 1), 256)
        assert imIn.getpixel((0, 0)) == min(256, maximum)

        imIn.putpixel((0, 0), 512)
        assert imIn.getpixel((0, 0)) == min(512, maximum)

    basic("L")

    basic("I;16")
    basic("I;16B")
    basic("I;16L")

    basic("I")


def test_tobytes():
    def tobytes(mode):
        return Image.new(mode, (1, 1), 1).tobytes()

    order = 1 if Image._ENDIAN == "<" else -1

    assert tobytes("L") == b"\x01"
    assert tobytes("I;16") == b"\x01\x00"
    assert tobytes("I;16B") == b"\x00\x01"
    assert tobytes("I") == b"\x01\x00\x00\x00"[::order]


def test_convert():

    im = original.copy()

    verify(im.convert("I;16"))
    verify(im.convert("I;16").convert("L"))
    verify(im.convert("I;16").convert("I"))

    verify(im.convert("I;16B"))
    verify(im.convert("I;16B").convert("L"))
    verify(im.convert("I;16B").convert("I"))
