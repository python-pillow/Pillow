from tester import *

from PIL import Image

# sample ppm stream
file = "Images/lena.ppm"
data = open(file, "rb").read()

def test_sanity():
    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "PPM")

def test_16bit_pgm():
    im = Image.open('Tests/images/16_bit_binary.pgm')
    im.load()
    assert_equal(im.mode, 'I')
    assert_equal(im.size, (20,100))

    tgt = Image.open('Tests/images/16_bit_binary_pgm.png')
    assert_image_equal(im, tgt)


def test_16bit_pgm_write():
    im = Image.open('Tests/images/16_bit_binary.pgm')
    im.load()

    f = tempfile('temp.pgm')
    assert_no_exception(lambda: im.save(f, 'PPM'))

    reloaded = Image.open(f)
    assert_image_equal(im, reloaded)


