from tester import *

from PIL import Image, FontFile, PcfFontFile
from PIL import ImageFont, ImageDraw

fontname = "Tests/fonts/helvO18.pcf"
tempname = tempfile("temp.pil", "temp.pbm")

message  = "hello, world"

def test_sanity():

    file = open(fontname, "rb")
    font = PcfFontFile.PcfFontFile(file)
    assert_true(isinstance(font, FontFile.FontFile))
    assert_equal(len([_f for _f in font.glyph if _f]), 192)

    font.save(tempname)

def test_draw():

    font = ImageFont.load(tempname)
    image = Image.new("L", font.getsize(message), "white")
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), message, font=font)
    # assert_signature(image, "7216c60f988dea43a46bb68321e3c1b03ec62aee")
