import pytest

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


@pytest.mark.parametrize("mode", ("L", "I;16", "I;16B", "I;16L", "I"))
def test_basic(tmp_path, mode):
    # PIL 1.1 has limited support for 16-bit image data.  Check that
    # create/copy/transform and save works as expected.

    im_in = original.convert(mode)
    verify(im_in)

    w, h = im_in.size

    im_out = im_in.copy()
    verify(im_out)  # copy

    im_out = im_in.transform((w, h), Image.Transform.EXTENT, (0, 0, w, h))
    verify(im_out)  # transform

    filename = str(tmp_path / "temp.im")
    im_in.save(filename)

    with Image.open(filename) as im_out:
        verify(im_in)
        verify(im_out)

    im_out = im_in.crop((0, 0, w, h))
    verify(im_out)

    im_out = Image.new(mode, (w, h), None)
    im_out.paste(im_in.crop((0, 0, w // 2, h)), (0, 0))
    im_out.paste(im_in.crop((w // 2, 0, w, h)), (w // 2, 0))

    verify(im_in)
    verify(im_out)

    im_in = Image.new(mode, (1, 1), 1)
    assert im_in.getpixel((0, 0)) == 1

    im_in.putpixel((0, 0), 2)
    assert im_in.getpixel((0, 0)) == 2

    if mode == "L":
        maximum = 255
    else:
        maximum = 32767

    im_in = Image.new(mode, (1, 1), 256)
    assert im_in.getpixel((0, 0)) == min(256, maximum)

    im_in.putpixel((0, 0), 512)
    assert im_in.getpixel((0, 0)) == min(512, maximum)


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

    for mode in ("I;16", "I;16B", "I;16N"):
        verify(im.convert(mode))
        verify(im.convert(mode).convert("L"))
        verify(im.convert(mode).convert("I"))
