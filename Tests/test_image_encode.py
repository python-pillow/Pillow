from __future__ import annotations

import pytest

from PIL import Image


@pytest.mark.parametrize(
    "mode",
    ("1", "L", "P", "LA", "I", "F", "I;16", "RGB", "RGBA", "CMYK"),
)
def test_raw_encoder_optimal_bufsize(mode: str) -> None:
    # Test the raw encoder does know the exact buffer size.
    im = Image.new(mode, (300, 200))
    encoder = Image._getencoder(mode, "raw", mode)
    encoder.setimage(im.im, (0, 0) + im.size)
    assert encoder.optimal_bufsize == len(im.tobytes())


def test_raw_encoder_optimal_bufsize_stride() -> None:
    im = Image.new("RGB", (100, 50))
    encoder = Image._getencoder("RGB", "raw", ("RGB", 400))
    encoder.setimage(im.im, (0, 0) + im.size)
    assert encoder.optimal_bufsize == 400 * 50
    encoder.encode(400)  # The encoder's internals change here
    # ... but the result for this should remain the same.
    assert encoder.optimal_bufsize == 400 * 50


def test_encoder_optimal_bufsize_unknown() -> None:
    im = Image.new("1", (64, 64))

    # the size is not known before the image has been assigned
    encoder = Image._getencoder("1", "raw", "1")
    assert encoder.optimal_bufsize == 0

    # nor for encoders whose output size depends on the pixel data
    encoder = Image._getencoder("1", "xbm", "1")
    encoder.setimage(im.im, (0, 0) + im.size)
    assert encoder.optimal_bufsize == 0
