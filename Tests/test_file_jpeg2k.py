import re
from io import BytesIO

import pytest

from PIL import Image, ImageFile, Jpeg2KImagePlugin, features

from .helper import (
    assert_image_equal,
    assert_image_similar,
    is_big_endian,
    skip_unless_feature,
)

pytestmark = skip_unless_feature("jpg_2000")

test_card = Image.open("Tests/images/test-card.png")
test_card.load()

# OpenJPEG 2.0.0 outputs this debugging message sometimes; we should
# ignore it---it doesn't represent a test failure.
# 'Not enough memory to handle tile data'


def roundtrip(im, **options):
    out = BytesIO()
    im.save(out, "JPEG2000", **options)
    test_bytes = out.tell()
    out.seek(0)
    im = Image.open(out)
    im.bytes = test_bytes  # for testing only
    im.load()
    return im


def test_sanity():
    # Internal version number
    assert re.search(r"\d+\.\d+\.\d+$", features.version_codec("jpg_2000"))

    with Image.open("Tests/images/test-card-lossless.jp2") as im:
        px = im.load()
        assert px[0, 0] == (0, 0, 0)
        assert im.mode == "RGB"
        assert im.size == (640, 480)
        assert im.format == "JPEG2000"
        assert im.get_format_mimetype() == "image/jp2"


def test_jpf():
    with Image.open("Tests/images/balloon.jpf") as im:
        assert im.format == "JPEG2000"
        assert im.get_format_mimetype() == "image/jpx"


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        Jpeg2KImagePlugin.Jpeg2KImageFile(invalid_file)


def test_bytesio():
    with open("Tests/images/test-card-lossless.jp2", "rb") as f:
        data = BytesIO(f.read())
    with Image.open(data) as im:
        im.load()
        assert_image_similar(im, test_card, 1.0e-3)


# These two test pre-written JPEG 2000 files that were not written with
# PIL (they were made using Adobe Photoshop)


def test_lossless(tmp_path):
    with Image.open("Tests/images/test-card-lossless.jp2") as im:
        im.load()
        outfile = str(tmp_path / "temp_test-card.png")
        im.save(outfile)
    assert_image_similar(im, test_card, 1.0e-3)


def test_lossy_tiled():
    with Image.open("Tests/images/test-card-lossy-tiled.jp2") as im:
        im.load()
        assert_image_similar(im, test_card, 2.0)


def test_lossless_rt():
    im = roundtrip(test_card)
    assert_image_equal(im, test_card)


def test_lossy_rt():
    im = roundtrip(test_card, quality_layers=[20])
    assert_image_similar(im, test_card, 2.0)


def test_tiled_rt():
    im = roundtrip(test_card, tile_size=(128, 128))
    assert_image_equal(im, test_card)


def test_tiled_offset_rt():
    im = roundtrip(test_card, tile_size=(128, 128), tile_offset=(0, 0), offset=(32, 32))
    assert_image_equal(im, test_card)


def test_tiled_offset_too_small():
    with pytest.raises(ValueError):
        roundtrip(test_card, tile_size=(128, 128), tile_offset=(0, 0), offset=(128, 32))


def test_irreversible_rt():
    im = roundtrip(test_card, irreversible=True, quality_layers=[20])
    assert_image_similar(im, test_card, 2.0)


def test_prog_qual_rt():
    im = roundtrip(test_card, quality_layers=[60, 40, 20], progression="LRCP")
    assert_image_similar(im, test_card, 2.0)


def test_prog_res_rt():
    im = roundtrip(test_card, num_resolutions=8, progression="RLCP")
    assert_image_equal(im, test_card)


def test_reduce():
    with Image.open("Tests/images/test-card-lossless.jp2") as im:
        assert callable(im.reduce)

        im.reduce = 2
        assert im.reduce == 2

        im.load()
        assert im.size == (160, 120)

        im.thumbnail((40, 40))
        assert im.size == (40, 30)


def test_layers_type(tmp_path):
    outfile = str(tmp_path / "temp_layers.jp2")
    for quality_layers in [[100, 50, 10], (100, 50, 10), None]:
        test_card.save(outfile, quality_layers=quality_layers)

    for quality_layers in ["quality_layers", ("100", "50", "10")]:
        with pytest.raises(ValueError):
            test_card.save(outfile, quality_layers=quality_layers)


def test_layers():
    out = BytesIO()
    test_card.save(out, "JPEG2000", quality_layers=[100, 50, 10], progression="LRCP")
    out.seek(0)

    with Image.open(out) as im:
        im.layers = 1
        im.load()
        assert_image_similar(im, test_card, 13)

    out.seek(0)
    with Image.open(out) as im:
        im.layers = 3
        im.load()
        assert_image_similar(im, test_card, 0.4)


def test_rgba():
    # Arrange
    with Image.open("Tests/images/rgb_trns_ycbc.j2k") as j2k:
        with Image.open("Tests/images/rgb_trns_ycbc.jp2") as jp2:

            # Act
            j2k.load()
            jp2.load()

            # Assert
            assert j2k.mode == "RGBA"
            assert jp2.mode == "RGBA"


def test_16bit_monochrome_has_correct_mode():
    with Image.open("Tests/images/16bit.cropped.j2k") as j2k:
        j2k.load()
        assert j2k.mode == "I;16"

    with Image.open("Tests/images/16bit.cropped.jp2") as jp2:
        jp2.load()
        assert jp2.mode == "I;16"


@pytest.mark.xfail(is_big_endian(), reason="Fails on big-endian")
def test_16bit_monochrome_jp2_like_tiff():
    with Image.open("Tests/images/16bit.cropped.tif") as tiff_16bit:
        with Image.open("Tests/images/16bit.cropped.jp2") as jp2:
            assert_image_similar(jp2, tiff_16bit, 1e-3)


@pytest.mark.xfail(is_big_endian(), reason="Fails on big-endian")
def test_16bit_monochrome_j2k_like_tiff():
    with Image.open("Tests/images/16bit.cropped.tif") as tiff_16bit:
        with Image.open("Tests/images/16bit.cropped.j2k") as j2k:
            assert_image_similar(j2k, tiff_16bit, 1e-3)


def test_16bit_j2k_roundtrips():
    with Image.open("Tests/images/16bit.cropped.j2k") as j2k:
        im = roundtrip(j2k)
        assert_image_equal(im, j2k)


def test_16bit_jp2_roundtrips():
    with Image.open("Tests/images/16bit.cropped.jp2") as jp2:
        im = roundtrip(jp2)
        assert_image_equal(im, jp2)


def test_unbound_local():
    # prepatch, a malformed jp2 file could cause an UnboundLocalError exception.
    with pytest.raises(OSError):
        Image.open("Tests/images/unbound_variable.jp2")


def test_parser_feed():
    # Arrange
    with open("Tests/images/test-card-lossless.jp2", "rb") as f:
        data = f.read()

    # Act
    p = ImageFile.Parser()
    p.feed(data)

    # Assert
    assert p.image.size == (640, 480)
