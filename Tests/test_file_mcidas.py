from __future__ import annotations

import struct
from pathlib import Path

import pytest

from PIL import Image, McIdasImagePlugin

from .helper import assert_image_equal_tofile


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(invalid_file)


def test_undersized_stride(tmp_path: Path) -> None:
    # A crafted area descriptor declares a row stride far smaller than a full
    # row of pixels. Memory mapping must not lay out row pointers at that
    # stride, which would read past the mapped buffer; the image is rejected
    # instead of leaking memory or crashing.
    words = [0] * 65
    words[2] = 4  # magic: 00 00 00 00 00 00 00 04
    words[9] = 1  # ysize
    words[10] = 200000  # xsize -> a full row is 200000 bytes (mode "L")
    words[11] = 1  # mode "L"
    words[14] = 0  # zeroes the xsize term of the stride
    words[15] = 1  # stride = 1  (much smaller than a row)
    data = struct.pack("!64i", *words[1:65])

    path = tmp_path / "undersized_stride.area"
    path.write_bytes(data)

    with Image.open(path) as im:
        with pytest.raises(ValueError, match="buffer is not large enough"):
            im.load()


def test_valid_file() -> None:
    # Arrange
    # https://ghrc.nsstc.nasa.gov/hydro/details/cmx3g8
    # https://ghrc.nsstc.nasa.gov/pub/fieldCampaigns/camex3/cmx3g8/browse/
    test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"
    saved_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.tiff"

    # Act
    with Image.open(test_file) as im:
        im.load()

        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "I;16B"
        assert im.size == (1800, 400)
        assert_image_equal_tofile(im, saved_file)
