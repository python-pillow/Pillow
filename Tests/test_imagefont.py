from tester import *

from PIL import Image
from io import BytesIO

try:
    from PIL import ImageFont
    ImageFont.core.getfont # check if freetype is available
except ImportError:
    skip()

def test_sanity():
    assert_match(ImageFont.core.freetype2_version, "\d+\.\d+\.\d+$")

def test_font_with_name():
    font_name = "Tests/fonts/FreeMono.ttf"
    font_size = 10
    assert_no_exception(lambda: ImageFont.truetype(font_name, font_size))

def test_font_with_filelike():
    font_name = "Tests/fonts/FreeMono.ttf"
    font_filelike = BytesIO(open(font_name, 'rb').read())
    font_size = 10
    assert_no_exception(lambda: ImageFont.truetype(font_filelike, font_size))

def test_font_old_parameters():
    font_name = "Tests/fonts/FreeMono.ttf"
    font_size = 10
    assert_warning(DeprecationWarning, lambda: ImageFont.truetype(filename=font_name, size=font_size))

