from __future__ import annotations

from io import BytesIO

import pytest

from PIL import EpsImagePlugin, Image, ImageFile
from Tests.helper import (
    assert_image,
    assert_image_equal,
    assert_image_similar,
    hopper,
    skip_unless_feature,
)


@pytest.fixture(scope="module")
def hopper_l_1k() -> Image.Image:
    return hopper("L").resize((1000, 1000), Image.Resampling.NEAREST)


def roundtrip(im: Image.Image, format: str) -> tuple[Image.Image, Image.Image]:
    if format in ("MSP", "XBM"):
        im = im.convert("1")

    test_file = BytesIO()

    im.copy().save(test_file, format)

    data = test_file.getvalue()

    parser = ImageFile.Parser()
    parser.feed(data)
    im_out = parser.close()

    return im, im_out


@pytest.mark.parametrize(
    "format",
    [
        "BMP",
        pytest.param(
            "EPS",
            marks=pytest.mark.skipif(
                not EpsImagePlugin.has_ghostscript(),
                reason="Ghostscript not available",
            ),
        ),
        "GIF",
        "IM",
        pytest.param("JPEG", marks=skip_unless_feature("jpg")),
        "MSP",
        "PCX",
        pytest.param("PNG", marks=skip_unless_feature("zlib")),
        "PPM",
        "TGA",
        "TIFF",
        "XBM",
    ],
)
def test_parser(
    monkeypatch: pytest.MonkeyPatch, hopper_l_1k: Image.Image, format: str
) -> None:
    # force multiple blocks in PNG driver
    monkeypatch.setattr(ImageFile, "MAXBLOCK", 8192)

    if format == "IM":
        with pytest.warns(DeprecationWarning, match="IM image format"):
            im1, im2 = roundtrip(hopper_l_1k, format)
    else:
        im1, im2 = roundtrip(hopper_l_1k, format)

    if format == "GIF":
        assert_image_similar(im1.convert("P"), im2, 1)
    elif format == "EPS":
        # This test fails on Ubuntu 12.04, PPC (Bigendian) It
        # appears to be a ghostscript 9.05 bug, since the
        # ghostscript rendering is wonky and the file is identical
        # to that written on ubuntu 12.04 x64
        # md5sum: ba974835ff2d6f3f2fd0053a23521d4a

        # EPS comes back in RGB:
        assert_image_similar(im1, im2.convert("L"), 20)
    elif format == "JPEG":  # Lossy compression
        assert_image(im1, im2.mode, im2.size)
    else:
        assert_image_equal(im1, im2)


def test_parser_pdf_roundtrip_error(hopper_l_1k: Image.Image) -> None:
    # See https://github.com/python-pillow/Pillow/issues/78
    with pytest.raises(OSError, match="cannot parse this image"):
        roundtrip(hopper_l_1k, "PDF")
