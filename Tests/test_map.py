import sys

import pytest

from PIL import Image


def test_overflow():
    # There is the potential to overflow comparisons in map.c
    # if there are > SIZE_MAX bytes in the image or if
    # the file encodes an offset that makes
    # (offset + size(bytes)) > SIZE_MAX

    # Note that this image triggers the decompression bomb warning:
    max_pixels = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = None

    # This image hits the offset test.
    with Image.open("Tests/images/l2rgb_read.bmp") as im:
        with pytest.raises((ValueError, MemoryError, OSError)):
            im.load()

    Image.MAX_IMAGE_PIXELS = max_pixels


def test_tobytes():
    # Note that this image triggers the decompression bomb warning:
    max_pixels = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = None

    # Previously raised an access violation on Windows
    with Image.open("Tests/images/l2rgb_read.bmp") as im:
        with pytest.raises((ValueError, MemoryError, OSError)):
            im.tobytes()

    Image.MAX_IMAGE_PIXELS = max_pixels


@pytest.mark.skipif(sys.maxsize <= 2 ** 32, reason="Requires 64-bit system")
def test_ysize():
    numpy = pytest.importorskip("numpy", reason="NumPy not installed")

    # Should not raise 'Integer overflow in ysize'
    arr = numpy.zeros((46341, 46341), dtype=numpy.uint8)
    Image.fromarray(arr)
