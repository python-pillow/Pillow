from tester import *

from PIL import Image, TarIO

codecs = dir(Image.core)
if "zip_decoder" not in codecs and "jpeg_decoder" not in codecs:
    skip("neither jpeg nor zip support not available")

# sample ppm stream
tarfile = "Images/lena.tar"

def test_sanity():
    if "zip_decoder" in codecs:
        tar = TarIO.TarIO(tarfile, 'lena.png')
        im = Image.open(tar)
        im.load()
        assert_equal(im.mode, "RGB")
        assert_equal(im.size, (128, 128))
        assert_equal(im.format, "PNG")

    if "jpeg_decoder" in codecs:
        tar = TarIO.TarIO(tarfile, 'lena.jpg')
        im = Image.open(tar)
        im.load()
        assert_equal(im.mode, "RGB")
        assert_equal(im.size, (128, 128))
        assert_equal(im.format, "JPEG")

