from tester import *

from PIL import Image, TarIO

# sample ppm stream
tarfile = "Images/lena.tar"

def test_sanity():
    tar = TarIO.TarIO(tarfile, 'lena.png')
    im = Image.open(tar)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "PNG")

    tar = TarIO.TarIO(tarfile, 'lena.jpg')
    im = Image.open(tar)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "JPEG")

