from tester import *

from PIL import Image
import io

def roundtrip(im):
    outfile = tempfile("temp.bmp")

    im.save(outfile, 'BMP')

    reloaded = Image.open(outfile)
    reloaded.load()
    assert_equal(im.mode, reloaded.mode)
    assert_equal(im.size, reloaded.size)
    assert_equal(reloaded.format, "BMP")


def test_sanity():
    roundtrip(lena())
    
    roundtrip(lena("1"))
    roundtrip(lena("L"))
    roundtrip(lena("P"))
    roundtrip(lena("RGB"))


def test_save_to_bytes():
    output = io.BytesIO()
    im = lena()
    im.save(output, "BMP")

    output.seek(0)
    reloaded = Image.open(output)
    
    assert_equal(im.mode, reloaded.mode)
    assert_equal(im.size, reloaded.size)
    assert_equal(reloaded.format, "BMP")
    
