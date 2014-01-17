from tester import *

from PIL import Image


try:
    from PIL import _webp
except:
    skip('webp support not installed')


if (_webp.WebPDecoderVersion() < 0x0200):
    skip('lossless not included')

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



