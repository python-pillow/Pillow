from tester import *

from PIL import Image
from PIL import ImageFile

codecs = dir(Image.core)

if "jpeg2k_encoder" not in codecs or "jpeg2k_decoder" not in codecs:
    skip('JPEG 2000 support not available')

# OpenJPEG 2.0.0 outputs this debugging message sometimes; we should
# ignore it---it doesn't represent a test failure.
ignore('Not enough memory to handle tile data')

test_card = Image.open('Tests/images/test-card.png')
test_card.load()

def roundtrip(im, **options):
    out = BytesIO()
    im.save(out, "JPEG2000", **options)
    bytes = out.tell()
    out.seek(0)
    im = Image.open(out)
    im.bytes = bytes # for testing only
    im.load()
    return im

# ----------------------------------------------------------------------

def test_sanity():
    # Internal version number
    assert_match(Image.core.jp2klib_version, '\d+\.\d+\.\d+$')

    im = Image.open('Tests/images/test-card-lossless.jp2')
    im.load()
    assert_equal(im.mode, 'RGB')
    assert_equal(im.size, (640, 480))
    assert_equal(im.format, 'JPEG2000')
    
# ----------------------------------------------------------------------

# These two test pre-written JPEG 2000 files that were not written with
# PIL (they were made using Adobe Photoshop)

def test_lossless():
    im = Image.open('Tests/images/test-card-lossless.jp2')
    im.load()
    im.save('/tmp/test-card.png')
    assert_image_similar(im, test_card, 1.0e-3)

def test_lossy_tiled():
    im = Image.open('Tests/images/test-card-lossy-tiled.jp2')
    im.load()
    assert_image_similar(im, test_card, 2.0)

# ----------------------------------------------------------------------

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
    im = roundtrip(test_card, tile_size=(128, 128), tile_offset=(0, 0),
                   offset=(32, 32))
    assert_image_equal(im, test_card)
    
def test_irreversible_rt():
    im = roundtrip(test_card, irreversible=True, quality_layers=[20])
    assert_image_similar(im, test_card, 2.0)

def test_prog_qual_rt():
    im = roundtrip(test_card, quality_layers=[60, 40, 20], progression='LRCP')
    assert_image_similar(im, test_card, 2.0)

def test_prog_res_rt():
    im = roundtrip(test_card, num_resolutions=8, progression='RLCP')
    assert_image_equal(im, test_card)

# ----------------------------------------------------------------------

def test_reduce():
    im = Image.open('Tests/images/test-card-lossless.jp2')
    im.reduce = 2
    im.load()
    assert_equal(im.size, (160, 120))

def test_layers():
    out = BytesIO()
    test_card.save(out, 'JPEG2000', quality_layers=[100, 50, 10],
                   progression='LRCP')
    out.seek(0)
    
    im = Image.open(out)
    im.layers = 1
    im.load()
    assert_image_similar(im, test_card, 13)

    out.seek(0)
    im = Image.open(out)
    im.layers = 3
    im.load()
    assert_image_similar(im, test_card, 0.4)
