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


def test_little_endian():
	im = Image.open('Tests/images/16bit.cropped.tif')
	assert_equal(im.getpixel((0,0)), 480)
	assert_equal(im.mode, 'I;16')

	b = im.tobytes()
	# Bytes are in image native order (little endian)
	if py3:
		assert_equal(b[0], ord(b'\xe0'))
		assert_equal(b[1], ord(b'\x01'))
	else:
		assert_equal(b[0], b'\xe0')
		assert_equal(b[1], b'\x01')
		

def test_big_endian():
	im = Image.open('Tests/images/16bit.MM.cropped.tif')
	assert_equal(im.getpixel((0,0)), 480)
	assert_equal(im.mode, 'I;16B')

	b = im.tobytes()

	# Bytes are in image native order (big endian)
	if py3:
		assert_equal(b[0], ord(b'\x01'))
		assert_equal(b[1], ord(b'\xe0'))
	else:
		assert_equal(b[0], b'\x01')
		assert_equal(b[1], b'\xe0')


def test_12bit_rawmode():
    """ Are we generating the same interpretation of the image as Imagemagick is? """

    #Image.DEBUG = True
    im = Image.open('Tests/images/12bit.cropped.tif')

    # to make the target --
    # convert 12bit.cropped.tif -depth 16 tmp.tif
    # convert tmp.tif -evaluate RightShift 4 12in16bit2.tif
    # imagemagick will auto scale so that a 12bit FFF is 16bit FFF0,
    # so we need to unshift so that the integer values are the same. 
    
    im2 = Image.open('Tests/images/12in16bit.tif')

    if Image.DEBUG:
        print (im.getpixel((0,0)))
        print (im.getpixel((0,1)))
        print (im.getpixel((0,2)))

        print (im2.getpixel((0,0)))
        print (im2.getpixel((0,1)))
        print (im2.getpixel((0,2)))
  
    assert_image_equal(im, im2)
