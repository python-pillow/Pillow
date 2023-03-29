import os
import re
from io import BytesIO

import pytest

from PIL import (
    Image,
    ImageFile,
    Jpeg2KImagePlugin,
    UnidentifiedImageError,
    _binary,
    features,
)

from .helper import (
    assert_image_equal,
    assert_image_similar,
    assert_image_similar_tofile,
    skip_unless_feature,
    skip_unless_feature_version,
)

EXTRA_DIR = "Tests/images/jpeg2000"

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
    with Image.open(out) as im:
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
    assert_image_similar_tofile(test_card, data, 1.0e-3)


# These two test pre-written JPEG 2000 files that were not written with
# PIL (they were made using Adobe Photoshop)


def test_lossless(tmp_path):
    with Image.open("Tests/images/test-card-lossless.jp2") as im:
        im.load()
        outfile = str(tmp_path / "temp_test-card.png")
        im.save(outfile)
    assert_image_similar(im, test_card, 1.0e-3)


def test_lossy_tiled():
    assert_image_similar_tofile(
        test_card, "Tests/images/test-card-lossy-tiled.jp2", 2.0
    )


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


@pytest.mark.parametrize("num_resolutions", range(2, 6))
def test_default_num_resolutions(num_resolutions):
    d = 1 << (num_resolutions - 1)
    im = test_card.resize((d - 1, d - 1))
    with pytest.raises(OSError):
        roundtrip(im, num_resolutions=num_resolutions)
    reloaded = roundtrip(im)
    assert_image_equal(im, reloaded)


def test_reduce():
    with Image.open("Tests/images/test-card-lossless.jp2") as im:
        assert callable(im.reduce)

        im.reduce = 2
        assert im.reduce == 2

        im.load()
        assert im.size == (160, 120)

        im.thumbnail((40, 40))
        assert im.size == (40, 30)


def test_load_dpi():
    with Image.open("Tests/images/test-card-lossless.jp2") as im:
        assert im.info["dpi"] == (71.9836, 71.9836)

    with Image.open("Tests/images/zero_dpi.jp2") as im:
        assert "dpi" not in im.info


def test_restricted_icc_profile():
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    try:
        # JPEG2000 image with a restricted ICC profile and a known colorspace
        with Image.open("Tests/images/balloon_eciRGBv2_aware.jp2") as im:
            assert im.mode == "RGB"
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False


def test_header_errors():
    for path in (
        "Tests/images/invalid_header_length.jp2",
        "Tests/images/not_enough_data.jp2",
    ):
        with pytest.raises(UnidentifiedImageError):
            with Image.open(path):
                pass

    with pytest.raises(OSError):
        with Image.open("Tests/images/expected_to_read.jp2"):
            pass


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


@pytest.mark.parametrize(
    "name, args, offset, data",
    (
        ("foo.j2k", {}, 0, b"\xff\x4f"),
        ("foo.jp2", {}, 4, b"jP"),
        (None, {"no_jp2": True}, 0, b"\xff\x4f"),
        ("foo.j2k", {"no_jp2": True}, 0, b"\xff\x4f"),
        ("foo.jp2", {"no_jp2": True}, 0, b"\xff\x4f"),
        ("foo.j2k", {"no_jp2": False}, 0, b"\xff\x4f"),
        ("foo.jp2", {"no_jp2": False}, 4, b"jP"),
        ("foo.jp2", {"no_jp2": False}, 4, b"jP"),
    ),
)
def test_no_jp2(name, args, offset, data):
    out = BytesIO()
    if name:
        out.name = name
    test_card.save(out, "JPEG2000", **args)
    out.seek(offset)
    assert out.read(2) == data


def test_mct():
    # Three component
    for val in (0, 1):
        out = BytesIO()
        test_card.save(out, "JPEG2000", mct=val, no_jp2=True)

        assert out.getvalue()[59] == val
        with Image.open(out) as im:
            assert_image_similar(im, test_card, 1.0e-3)

    # Single component should have MCT disabled
    for val in (0, 1):
        out = BytesIO()
        with Image.open("Tests/images/16bit.cropped.jp2") as jp2:
            jp2.save(out, "JPEG2000", mct=val, no_jp2=True)

        assert out.getvalue()[53] == 0
        with Image.open(out) as im:
            assert_image_similar(im, jp2, 1.0e-3)


def test_sgnd(tmp_path):
    outfile = str(tmp_path / "temp.jp2")

    im = Image.new("L", (1, 1))
    im.save(outfile)
    with Image.open(outfile) as reloaded:
        assert reloaded.getpixel((0, 0)) == 0

    im = Image.new("L", (1, 1))
    im.save(outfile, signed=True)
    with Image.open(outfile) as reloaded_signed:
        assert reloaded_signed.getpixel((0, 0)) == 128


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


@pytest.mark.parametrize("ext", (".j2k", ".jp2"))
def test_16bit_monochrome_has_correct_mode(ext):
    with Image.open("Tests/images/16bit.cropped" + ext) as im:
        im.load()
        assert im.mode == "I;16"


def test_16bit_monochrome_jp2_like_tiff():
    with Image.open("Tests/images/16bit.cropped.tif") as tiff_16bit:
        assert_image_similar_tofile(tiff_16bit, "Tests/images/16bit.cropped.jp2", 1e-3)


def test_16bit_monochrome_j2k_like_tiff():
    with Image.open("Tests/images/16bit.cropped.tif") as tiff_16bit:
        assert_image_similar_tofile(tiff_16bit, "Tests/images/16bit.cropped.j2k", 1e-3)


def test_16bit_j2k_roundtrips():
    with Image.open("Tests/images/16bit.cropped.j2k") as j2k:
        im = roundtrip(j2k)
        assert_image_equal(im, j2k)


def test_16bit_jp2_roundtrips():
    with Image.open("Tests/images/16bit.cropped.jp2") as jp2:
        im = roundtrip(jp2)
        assert_image_equal(im, jp2)


def test_issue_6194():
    with Image.open("Tests/images/issue_6194.j2k") as im:
        assert im.getpixel((5, 5)) == 31


def test_unbound_local():
    # prepatch, a malformed jp2 file could cause an UnboundLocalError exception.
    with pytest.raises(OSError):
        with Image.open("Tests/images/unbound_variable.jp2"):
            pass


def test_parser_feed():
    # Arrange
    with open("Tests/images/test-card-lossless.jp2", "rb") as f:
        data = f.read()

    # Act
    p = ImageFile.Parser()
    p.feed(data)

    # Assert
    assert p.image.size == (640, 480)


@pytest.mark.skipif(
    not os.path.exists(EXTRA_DIR), reason="Extra image files not installed"
)
@pytest.mark.parametrize("name", ("subsampling_1", "subsampling_2", "zoo1", "zoo2"))
def test_subsampling_decode(name):
    test = f"{EXTRA_DIR}/{name}.jp2"
    reference = f"{EXTRA_DIR}/{name}.ppm"

    with Image.open(test) as im:
        epsilon = 3  # for YCbCr images
        with Image.open(reference) as im2:
            width, height = im2.size
            if name[-1] == "2":
                # RGB reference images are downscaled
                epsilon = 3e-3
                width, height = width * 2, height * 2
            expected = im2.resize((width, height), Image.Resampling.NEAREST)
        assert_image_similar(im, expected, epsilon)


def test_comment():
    with Image.open("Tests/images/comment.jp2") as im:
        assert im.info["comment"] == b"Created by OpenJPEG version 2.5.0"

    # Test an image that is truncated partway through a codestream
    with open("Tests/images/comment.jp2", "rb") as fp:
        b = BytesIO(fp.read(130))
        with Image.open(b) as im:
            pass


def test_save_comment():
    for comment in ("Created by Pillow", b"Created by Pillow"):
        out = BytesIO()
        test_card.save(out, "JPEG2000", comment=comment)

        with Image.open(out) as im:
            assert im.info["comment"] == b"Created by Pillow"

    out = BytesIO()
    long_comment = b" " * 65531
    test_card.save(out, "JPEG2000", comment=long_comment)
    with Image.open(out) as im:
        assert im.info["comment"] == long_comment

    with pytest.raises(ValueError):
        test_card.save(out, "JPEG2000", comment=long_comment + b" ")


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/crash-4fb027452e6988530aa5dabee76eecacb3b79f8a.j2k",
        "Tests/images/crash-7d4c83eb92150fb8f1653a697703ae06ae7c4998.j2k",
        "Tests/images/crash-ccca68ff40171fdae983d924e127a721cab2bd50.j2k",
        "Tests/images/crash-d2c93af851d3ab9a19e34503626368b2ecde9c03.j2k",
    ],
)
def test_crashes(test_file):
    with open(test_file, "rb") as f:
        with Image.open(f) as im:
            # Valgrind should not complain here
            try:
                im.load()
            except OSError:
                pass


@skip_unless_feature_version("jpg_2000", "2.4.0")
def test_plt_marker():
    # Search the start of the codesteam for PLT
    out = BytesIO()
    test_card.save(out, "JPEG2000", no_jp2=True, plt=True)
    out.seek(0)
    while True:
        marker = out.read(2)
        if not marker:
            assert False, "End of stream without PLT"

        jp2_boxid = _binary.i16be(marker)
        if jp2_boxid == 0xFF4F:
            # SOC has no length
            continue
        elif jp2_boxid == 0xFF58:
            # PLT
            return
        elif jp2_boxid == 0xFF93:
            assert False, "SOD without finding PLT first"

        hdr = out.read(2)
        length = _binary.i16be(hdr)
        out.seek(length - 2, os.SEEK_CUR)
