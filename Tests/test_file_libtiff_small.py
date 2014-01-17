from tester import *

from PIL import Image

from test_file_libtiff import _assert_noerr

codecs = dir(Image.core)

if "libtiff_encoder" not in codecs or "libtiff_decoder" not in codecs:
    skip("tiff support not available")

""" The small lena image was failing on open in the libtiff
    decoder because the file pointer was set to the wrong place
    by a spurious seek. It wasn't failing with the byteio method.

    It was fixed by forcing an lseek to the beginning of the
    file just before reading in libtiff. These tests remain
    to ensure that it stays fixed. """


def test_g4_lena_file():
    """Testing the open file load path"""

    file = "Tests/images/lena_g4.tif"
    with open(file,'rb') as f:
        im = Image.open(f)

        assert_equal(im.size, (128,128))
        _assert_noerr(im)

def test_g4_lena_bytesio():
    """Testing the bytesio loading code path"""
    from io import BytesIO
    file = "Tests/images/lena_g4.tif"
    s = BytesIO()
    with open(file,'rb') as f:
        s.write(f.read())
        s.seek(0)
    im = Image.open(s)

    assert_equal(im.size, (128,128))
    _assert_noerr(im)

def test_g4_lena():
    """The 128x128 lena image fails for some reason. Investigating"""

    file = "Tests/images/lena_g4.tif"
    im = Image.open(file)

    assert_equal(im.size, (128,128))
    _assert_noerr(im)

