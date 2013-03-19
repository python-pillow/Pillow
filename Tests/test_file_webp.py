from tester import *

from PIL import Image

def test_read():

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
    file = tempfile("temp.webp")

    lena("RGB").save(file)

    reloaded= Image.open(file)
    reloaded.load()

    assert_equal(reloaded.mode, "RGB")
    assert_equal(reloaded.size, (128, 128))
    assert_equal(reloaded.format, "WEBP")
    assert_no_exception(lambda: reloaded.load())
    assert_no_exception(lambda: reloaded.getdata())



