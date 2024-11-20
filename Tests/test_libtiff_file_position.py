from __future__ import annotations


import pytest

from PIL import Image


@pytest.mark.parametrize('test_file', [
    'Tests/images/old-style-jpeg-compression-no-samplesperpixel.tif',
    'Tests/images/old-style-jpeg-compression.tif',
])
def test_libtiff_exif_loading(test_file) -> None:
    # loading image before exif
    im1 = Image.open(open(test_file, 'rb', buffering=1048576))
    im1.load()
    exif1 = dict(im1.getexif())

    # loading exif before image
    im2 = Image.open(open(test_file, 'rb', buffering=1048576))
    exif2 = dict(im2.getexif())

    assert exif1 == exif2
