from tester import *

from PIL import Image

def test_read():
    """ Can we write a webp without error. Does it have the bits we expect?"""
    
    file = "Images/lena.webp"
    im = Image.open(file)

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "WEBP")
    assert_no_exception(lambda: im.load())
    assert_no_exception(lambda: im.getdata())

    orig_bytes  = im.tobytes()

    # generated with: dwebp -ppm ../../Images/lena.webp -o lena_webp_bits.ppm
    target = Image.open('Tests/images/lena_webp_bits.ppm')
    assert_image_equal(im, target)
    

def test_write():
    """ Can we write a webp without error. Does it have the bits we expect?"""

    file = tempfile("temp.webp")

    lena("RGB").save(file)

    im= Image.open(file)
    im.load()

    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "WEBP")
    assert_no_exception(lambda: im.load())
    assert_no_exception(lambda: im.getdata())

    # generated with: dwebp -ppm temp.webp -o lena_webp_write.ppm
    target = Image.open('Tests/images/lena_webp_write.ppm')
    assert_image_equal(im, target)

