from tester import *

from PIL import Image

def test_sanity():

    file = tempfile("temp.tif")

    lena("RGB").save(file)

    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "TIFF")

    lena("1").save(file)
    im = Image.open(file)

    lena("L").save(file)
    im = Image.open(file)

    lena("P").save(file)
    im = Image.open(file)

    lena("RGB").save(file)
    im = Image.open(file)

    lena("I").save(file)
    im = Image.open(file)

def test_mac_tiff():
    # Read RGBa images from Mac OS X [@PIL136]

    file = "Tests/images/pil136.tiff"
    im = Image.open(file)

    assert_equal(im.mode, "RGBA")
    assert_equal(im.size, (55, 43))
    assert_equal(im.tile, [('raw', (0, 0, 55, 43), 8, ('RGBa', 0, 1))])
    assert_no_exception(lambda: im.load())

def test_gimp_tiff():
    # Read TIFF JPEG images from GIMP [@PIL168]

    codecs = dir(Image.core)
    if "jpeg_decoder" not in codecs:
        skip("jpeg support not available")

    file = "Tests/images/pil168.tif"
    im = Image.open(file)

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (256, 256))
    assert_equal(im.tile, [
            ('jpeg', (0, 0, 256, 64), 8, ('RGB', '')),
            ('jpeg', (0, 64, 256, 128), 1215, ('RGB', '')),
            ('jpeg', (0, 128, 256, 192), 2550, ('RGB', '')),
            ('jpeg', (0, 192, 256, 256), 3890, ('RGB', '')),
            ])
    assert_no_exception(lambda: im.load())

def test_xyres_tiff():
    from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
    file = "Tests/images/pil168.tif"
    im = Image.open(file)
    assert isinstance(im.tag.tags[X_RESOLUTION][0], tuple)
    assert isinstance(im.tag.tags[Y_RESOLUTION][0], tuple)
    #Try to read a file where X,Y_RESOLUTION are ints
    im.tag.tags[X_RESOLUTION] = (72,)
    im.tag.tags[Y_RESOLUTION] = (72,)
    im._setup()
    assert_equal(im.info['dpi'], (72., 72.))
