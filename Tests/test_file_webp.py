from tester import *

from PIL import Image

try:
    import _webp
except:
    skip('webp support not installed')
		
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

    # If we're using the exact same version of webp, this test should pass.
    # but it doesn't if the webp is generated on Ubuntu and tested on Fedora.
    
    # generated with: dwebp -ppm temp.webp -o lena_webp_write.ppm
    #target = Image.open('Tests/images/lena_webp_write.ppm')
    #assert_image_equal(im, target)

    # This test asserts that the images are similar. If the average pixel difference
    # between the two images is less than the epsilon value, then we're going to
    # accept that it's a reasonable lossy version of the image. The included lena images
    # for webp are showing ~16 on Ubuntu, the jpegs are showing ~18. 
    target = lena('RGB')
    assert_image_similar(im, target, 20.0)


