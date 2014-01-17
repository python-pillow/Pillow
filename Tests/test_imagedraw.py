from tester import *

from PIL import Image
from PIL import ImageDraw

def test_sanity():

    im = lena("RGB").copy()

    draw = ImageDraw.ImageDraw(im)
    draw = ImageDraw.Draw(im)

    draw.ellipse(list(range(4)))
    draw.line(list(range(10)))
    draw.polygon(list(range(100)))
    draw.rectangle(list(range(4)))

    success()

def test_deprecated():

    im = lena().copy()

    draw = ImageDraw.Draw(im)

    assert_warning(DeprecationWarning, lambda: draw.setink(0))
    assert_warning(DeprecationWarning, lambda: draw.setfill(0))

