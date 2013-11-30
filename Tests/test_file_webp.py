from tester import *

from PIL import Image

try:
    from PIL import _webp
except:
    skip('webp support not installed')


def test_version():
    assert_no_exception(lambda: _webp.WebPDecoderVersion())

def test_good_alpha():
    assert_equal(_webp.WebPDecoderBuggyAlpha(), 0)


def test_read_rgb():

    file_path = "Images/lena.webp"
    image = Image.open(file_path)

    assert_equal(image.mode, "RGB")
    assert_equal(image.size, (128, 128))
    assert_equal(image.format, "WEBP")
    assert_no_exception(lambda: image.load())
    assert_no_exception(lambda: image.getdata())

    # generated with: dwebp -ppm ../../Images/lena.webp -o lena_webp_bits.ppm
    target = Image.open('Tests/images/lena_webp_bits.ppm')
    assert_image_equal(image, target)


def test_write_rgb():
    """
    Can we write a RGB mode file to webp without error. Does it have the bits we
    expect?

    """

    temp_file = tempfile("temp.webp")

    lena("RGB").save(temp_file)

    image = Image.open(temp_file)
    image.load()

    assert_equal(image.mode, "RGB")
    assert_equal(image.size, (128, 128))
    assert_equal(image.format, "WEBP")
    assert_no_exception(lambda: image.load())
    assert_no_exception(lambda: image.getdata())

    # If we're using the exact same version of webp, this test should pass.
    # but it doesn't if the webp is generated on Ubuntu and tested on Fedora.

    # generated with: dwebp -ppm temp.webp -o lena_webp_write.ppm
    #target = Image.open('Tests/images/lena_webp_write.ppm')
    #assert_image_equal(image, target)

    # This test asserts that the images are similar. If the average pixel difference
    # between the two images is less than the epsilon value, then we're going to
    # accept that it's a reasonable lossy version of the image. The included lena images
    # for webp are showing ~16 on Ubuntu, the jpegs are showing ~18.
    target = lena("RGB")
    assert_image_similar(image, target, 20.0)


def test_write_lossless_rgb():
    temp_file = tempfile("temp.webp")

    lena("RGB").save(temp_file, lossless=True)

    image = Image.open(temp_file)
    image.load()

    assert_equal(image.mode, "RGB")
    assert_equal(image.size, (128, 128))
    assert_equal(image.format, "WEBP")
    assert_no_exception(lambda: image.load())
    assert_no_exception(lambda: image.getdata())


    assert_image_equal(image, lena("RGB"))




def test_write_rgba():
    """
    Can we write a RGBA mode file to webp without error. Does it have the bits we
    expect?

    """

    temp_file = tempfile("temp.webp")

    pil_image = Image.new("RGBA", (10, 10), (255, 0, 0, 20))
    pil_image.save(temp_file)

    if _webp.WebPDecoderBuggyAlpha():
        return

    image = Image.open(temp_file)
    image.load()

    assert_equal(image.mode, "RGBA")
    assert_equal(image.size, (10, 10))
    assert_equal(image.format, "WEBP")
    assert_no_exception(image.load)
    assert_no_exception(image.getdata)

    assert_image_similar(image, pil_image, 1.0)

if _webp.WebPDecoderBuggyAlpha():
    skip("Buggy early version of webp installed, not testing transparency")

def test_read_rgba():
    # Generated with `cwebp transparent.png -o transparent.webp`
    file_path = "Images/transparent.webp"
    image = Image.open(file_path)

    assert_equal(image.mode, "RGBA")
    assert_equal(image.size, (200, 150))
    assert_equal(image.format, "WEBP")
    assert_no_exception(lambda: image.load())
    assert_no_exception(lambda: image.getdata())

    orig_bytes  = image.tobytes()

    target = Image.open('Images/transparent.png')
    assert_image_similar(image, target, 20.0)



def test_write_lossless_rgb():
    temp_file = tempfile("temp.webp")
    #temp_file = "temp.webp"
    
    pil_image = lena('RGBA')

    mask = Image.new("RGBA", (64, 64), (128,128,128,128))
    pil_image.paste(mask, (0,0), mask)   # add some partially transparent bits.
    
    pil_image.save(temp_file, lossless=True)
    
    image = Image.open(temp_file)
    image.load()

    assert_equal(image.mode, "RGBA")
    assert_equal(image.size, pil_image.size)
    assert_equal(image.format, "WEBP")
    assert_no_exception(lambda: image.load())
    assert_no_exception(lambda: image.getdata())


    assert_image_equal(image, pil_image)
