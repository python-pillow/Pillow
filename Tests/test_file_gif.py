from tester import *

from PIL import Image

codecs = dir(Image.core)

if "gif_encoder" not in codecs or "gif_decoder" not in codecs:
    skip("gif support not available") # can this happen?

# sample gif stream
file = "Images/lena.gif"
data = open(file, "rb").read()

def test_sanity():
    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "P")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "GIF")

def test_optimize():
    def test(optimize):
        im = Image.new("L", (1, 1), 0)
        file = BytesIO()
        im.save(file, "GIF", optimize=optimize)
        return len(file.getvalue())
    assert_equal(test(0), 800)
    assert_equal(test(1), 32)
