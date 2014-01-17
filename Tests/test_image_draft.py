from tester import *

from PIL import Image

codecs = dir(Image.core)

if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
    skip("jpeg support not available")

filename = "Images/lena.jpg"

data = tostring(Image.open(filename).resize((512, 512)), "JPEG")

def draft(mode, size):
    im = fromstring(data)
    im.draft(mode, size)
    return im

def test_size():
    assert_equal(draft("RGB", (512, 512)).size, (512, 512))
    assert_equal(draft("RGB", (256, 256)).size, (256, 256))
    assert_equal(draft("RGB", (128, 128)).size, (128, 128))
    assert_equal(draft("RGB", (64, 64)).size, (64, 64))
    assert_equal(draft("RGB", (32, 32)).size, (64, 64))

def test_mode():
    assert_equal(draft("1", (512, 512)).mode, "RGB")
    assert_equal(draft("L", (512, 512)).mode, "L")
    assert_equal(draft("RGB", (512, 512)).mode, "RGB")
    assert_equal(draft("YCbCr", (512, 512)).mode, "YCbCr")
