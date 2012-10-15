from tester import *

from PIL import Image
try:
    from PIL import ImageFont
    ImageFont.core.getfont # check if freetype is available
except ImportError:
    skip()

def test_sanity():

    assert_match(ImageFont.core.freetype2_version, "\d+\.\d+\.\d+$")
