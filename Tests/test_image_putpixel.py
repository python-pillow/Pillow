from tester import *

from PIL import Image

Image.USE_CFFI_ACCESS=False

def test_sanity():

    im1 = lena()
    im2 = Image.new(im1.mode, im1.size, 0)

    for y in range(im1.size[1]):
        for x in range(im1.size[0]):
            pos = x, y
            im2.putpixel(pos, im1.getpixel(pos))

    assert_image_equal(im1, im2)

    im2 = Image.new(im1.mode, im1.size, 0)
    im2.readonly = 1

    for y in range(im1.size[1]):
        for x in range(im1.size[0]):
            pos = x, y
            im2.putpixel(pos, im1.getpixel(pos))

    assert_false(im2.readonly)
    assert_image_equal(im1, im2)

    im2 = Image.new(im1.mode, im1.size, 0)

    pix1 = im1.load()
    pix2 = im2.load()

    for y in range(im1.size[1]):
        for x in range(im1.size[0]):
            pix2[x, y] = pix1[x, y]

    assert_image_equal(im1, im2)




# see test_image_getpixel for more tests

