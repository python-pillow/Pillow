from tester import *

from PIL import Image

try:
    from PIL import _webp
except:
    skip('webp support not installed')


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




