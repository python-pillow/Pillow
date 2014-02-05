from tester import *

from PIL import Image, FontFile, PcfFontFile
from PIL import ImageFont, ImageDraw

codecs = dir(Image.core)

if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
    skip("zlib support not available")

fontname = "Tests/fonts/helvO18.pcf"
tempname = tempfile("temp.pil", "temp.pbm")

message  = "hello, world"

def test_sanity():

    file = open(fontname, "rb")
    font = PcfFontFile.PcfFontFile(file)
    assert_true(isinstance(font, FontFile.FontFile))
    assert_equal(len([_f for _f in font.glyph if _f]), 192)

    font.save(tempname)

def xtest_draw():

    font = ImageFont.load(tempname)
    image = Image.new("L", font.getsize(message), "white")
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), message, font=font)
    # assert_signature(image, "7216c60f988dea43a46bb68321e3c1b03ec62aee")

def _test_high_characters(message):

    font = ImageFont.load(tempname)
    image = Image.new("L", font.getsize(message), "white")
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), message, font=font)

    compare = Image.open('Tests/images/high_ascii_chars.png')
    assert_image_equal(image, compare)

def test_high_characters():
    message = "".join([chr(i+1) for i in range(140,232)])
    _test_high_characters(message)
    # accept bytes instances in Py3. 
    if bytes is not str:
        _test_high_characters(message.encode('latin1'))

