from __future__ import annotations

import sys

import pytest

from PIL import Image


def test_overflow(monkeypatch: pytest.MonkeyPatch) -> None:
    # There is the potential to overflow comparisons in map.c
    # if there are > SIZE_MAX bytes in the image or if
    # the file encodes an offset that makes
    # (offset + size(bytes)) > SIZE_MAX

    # Note that this image triggers the decompression bomb warning:
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", None)

    # This image hits the offset test.
    with Image.open("Tests/images/l2rgb_read.bmp") as im:
        with pytest.raises((ValueError, MemoryError, OSError)):
            im.load()


def test_tobytes(monkeypatch: pytest.MonkeyPatch) -> None:
    # Note that this image triggers the decompression bomb warning:
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", None)

    # Previously raised an access violation on Windows
    with Image.open("Tests/images/l2rgb_read.bmp") as im:
        with pytest.raises((ValueError, MemoryError, OSError)):
            im.tobytes()


@pytest.mark.skipif(sys.maxsize <= 2**32, reason="Requires 64-bit system")
def test_ysize() -> None:
    numpy = pytest.importorskip("numpy", reason="NumPy not installed")

    # Should not raise 'Integer overflow in ysize'
    arr = numpy.zeros((46341, 46341), dtype=numpy.uint8)
    Image.fromarray(arr)
