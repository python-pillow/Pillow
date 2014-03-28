from tester import *

import random

from PIL import Image
from PIL import ImageFile

codecs = dir(Image.core)

if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
    skip("jpeg support not available")

test_file = "Images/lena.jpg"

def roundtrip(im, **options):
    out = BytesIO()
    im.save(out, "JPEG", **options)
    bytes = out.tell()
    out.seek(0)
    im = Image.open(out)
    im.bytes = bytes # for testing only
    return im

# --------------------------------------------------------------------

def test_sanity():

    # internal version number
    assert_match(Image.core.jpeglib_version, "\d+\.\d+$")

    im = Image.open(test_file)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "JPEG")

# --------------------------------------------------------------------

def test_app():
    # Test APP/COM reader (@PIL135)
    im = Image.open(test_file)
    assert_equal(im.applist[0],
                 ("APP0", b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"))
    assert_equal(im.applist[1], ("COM", b"Python Imaging Library"))
    assert_equal(len(im.applist), 2)

def test_cmyk():
    # Test CMYK handling.  Thanks to Tim and Charlie for test data,
    # Michael for getting me to look one more time.
    f = "Tests/images/pil_sample_cmyk.jpg"
    im = Image.open(f)
    # the source image has red pixels in the upper left corner.
    c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
    assert_true(c == 0.0 and m > 0.8 and y > 0.8 and k == 0.0)
    # the opposite corner is black
    c, m, y, k = [x / 255.0 for x in im.getpixel((im.size[0]-1, im.size[1]-1))]
    assert_true(k > 0.9)
    # roundtrip, and check again
    im = roundtrip(im)
    c, m, y, k = [x / 255.0 for x in im.getpixel((0, 0))]
    assert_true(c == 0.0 and m > 0.8 and y > 0.8 and k == 0.0)
    c, m, y, k = [x / 255.0 for x in im.getpixel((im.size[0]-1, im.size[1]-1))]
    assert_true(k > 0.9)

def test_dpi():
    def test(xdpi, ydpi=None):
        im = Image.open(test_file)
        im = roundtrip(im, dpi=(xdpi, ydpi or xdpi))
        return im.info.get("dpi")
    assert_equal(test(72), (72, 72))
    assert_equal(test(300), (300, 300))
    assert_equal(test(100, 200), (100, 200))
    assert_equal(test(0), None) # square pixels

def test_icc():
    # Test ICC support
    im1 = Image.open("Tests/images/rgb.jpg")
    icc_profile = im1.info["icc_profile"]
    assert_equal(len(icc_profile), 3144)
    # Roundtrip via physical file.
    f = tempfile("temp.jpg")
    im1.save(f, icc_profile=icc_profile)
    im2 = Image.open(f)
    assert_equal(im2.info.get("icc_profile"), icc_profile)
    # Roundtrip via memory buffer.
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), icc_profile=icc_profile)
    assert_image_equal(im1, im2)
    assert_false(im1.info.get("icc_profile"))
    assert_true(im2.info.get("icc_profile"))

def test_icc_big():
    # Make sure that the "extra" support handles large blocks
    def test(n):
        # The ICC APP marker can store 65519 bytes per marker, so
        # using a 4-byte test code should allow us to detect out of
        # order issues.
        icc_profile = (b"Test"*int(n/4+1))[:n]
        assert len(icc_profile) == n # sanity
        im1 = roundtrip(lena(), icc_profile=icc_profile)
        assert_equal(im1.info.get("icc_profile"), icc_profile or None)
    test(0); test(1)
    test(3); test(4); test(5)
    test(65533-14) # full JPEG marker block
    test(65533-14+1) # full block plus one byte
    test(ImageFile.MAXBLOCK) # full buffer block
    test(ImageFile.MAXBLOCK+1) # full buffer block plus one byte
    test(ImageFile.MAXBLOCK*4+3) # large block

def test_optimize():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), optimize=1)
    assert_image_equal(im1, im2)
    assert_true(im1.bytes >= im2.bytes)

def test_optimize_large_buffer():
    #https://github.com/python-imaging/Pillow/issues/148
    f = tempfile('temp.jpg')
    # this requires ~ 1.5x Image.MAXBLOCK
    im = Image.new("RGB", (4096,4096), 0xff3333)
    im.save(f, format="JPEG", optimize=True)

def test_progressive():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), progressive=True)
    assert_image_equal(im1, im2)
    assert_true(im1.bytes >= im2.bytes)

def test_progressive_large_buffer():
    f = tempfile('temp.jpg')
    # this requires ~ 1.5x Image.MAXBLOCK
    im = Image.new("RGB", (4096,4096), 0xff3333)
    im.save(f, format="JPEG", progressive=True)

def test_progressive_large_buffer_highest_quality():
    f = tempfile('temp.jpg')
    if py3:
        a = bytes(random.randint(0, 255) for _ in range(256 * 256 * 3))
    else:
        a = b''.join(chr(random.randint(0, 255)) for _ in range(256 * 256 * 3))
    im = Image.frombuffer("RGB", (256, 256), a, "raw", "RGB", 0, 1)
    # this requires more bytes than pixels in the image
    im.save(f, format="JPEG", progressive=True, quality=100)

def test_large_exif():
    #https://github.com/python-imaging/Pillow/issues/148
    f = tempfile('temp.jpg')
    im = lena()
    im.save(f,'JPEG', quality=90, exif=b"1"*65532)

def test_progressive_compat():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), progressive=1)
    im3 = roundtrip(lena(), progression=1) # compatibility
    assert_image_equal(im1, im2)
    assert_image_equal(im1, im3)
    assert_false(im1.info.get("progressive"))
    assert_false(im1.info.get("progression"))
    assert_true(im2.info.get("progressive"))
    assert_true(im2.info.get("progression"))
    assert_true(im3.info.get("progressive"))
    assert_true(im3.info.get("progression"))

def test_quality():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), quality=50)
    assert_image(im1, im2.mode, im2.size)
    assert_true(im1.bytes >= im2.bytes)

def test_smooth():
    im1 = roundtrip(lena())
    im2 = roundtrip(lena(), smooth=100)
    assert_image(im1, im2.mode, im2.size)

def test_subsampling():
    def getsampling(im):
        layer = im.layer
        return layer[0][1:3] + layer[1][1:3] + layer[2][1:3]
    # experimental API
    im = roundtrip(lena(), subsampling=-1) # default
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=0) # 4:4:4
    assert_equal(getsampling(im), (1, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=1) # 4:2:2
    assert_equal(getsampling(im), (2, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=2) # 4:1:1
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling=3) # default (undefined)
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))

    im = roundtrip(lena(), subsampling="4:4:4")
    assert_equal(getsampling(im), (1, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling="4:2:2")
    assert_equal(getsampling(im), (2, 1, 1, 1, 1, 1))
    im = roundtrip(lena(), subsampling="4:1:1")
    assert_equal(getsampling(im), (2, 2, 1, 1, 1, 1))

    assert_exception(TypeError, lambda: roundtrip(lena(), subsampling="1:1:1"))

def test_exif():
    im = Image.open("Tests/images/pil_sample_rgb.jpg")
    info = im._getexif()
    assert_equal(info[305], 'Adobe Photoshop CS Macintosh')


def test_quality_keep():
    im = Image.open("Images/lena.jpg")
    f = tempfile('temp.jpg')
    assert_no_exception(lambda: im.save(f, quality='keep'))
