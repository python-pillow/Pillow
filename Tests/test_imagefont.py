from tester import *

from PIL import Image
from io import BytesIO
import os

try:
    from PIL import ImageFont
    ImageFont.core.getfont # check if freetype is available
except ImportError:
    skip()

from PIL import ImageDraw

font_path = "Tests/fonts/FreeMono.ttf"
font_size=20

def test_sanity():
    assert_match(ImageFont.core.freetype2_version, "\d+\.\d+\.\d+$")

def test_font_with_name():
    assert_no_exception(lambda: ImageFont.truetype(font_path, font_size))
    assert_no_exception(lambda: _render(font_path))
    _clean()

def _font_as_bytes():
    with open(font_path, 'rb') as f:
        font_bytes = BytesIO(f.read())
    return font_bytes

def test_font_with_filelike():
    assert_no_exception(lambda: ImageFont.truetype(_font_as_bytes(), font_size))
    assert_no_exception(lambda: _render(_font_as_bytes()))
    # Usage note:  making two fonts from the same buffer fails.
    #shared_bytes = _font_as_bytes()
    #assert_no_exception(lambda: _render(shared_bytes))
    #assert_exception(Exception, lambda: _render(shared_bytes))
    _clean()

def test_font_with_open_file():
    with open(font_path, 'rb') as f:
        assert_no_exception(lambda: _render(f))
    _clean()

def test_font_old_parameters():
    assert_warning(DeprecationWarning, lambda: ImageFont.truetype(filename=font_path, size=font_size))

def _render(font):
    txt = "Hello World!"
    ttf = ImageFont.truetype(font, font_size)
    w, h = ttf.getsize(txt)
    img = Image.new("RGB", (256, 64), "white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), txt, font=ttf, fill='black')

    img.save('font.png')
    return img

def _clean():
    os.unlink('font.png')

def test_render_equal():
    img_path = _render(font_path)
    with open(font_path, 'rb') as f:
        font_filelike = BytesIO(f.read())
    img_filelike = _render(font_filelike)

    assert_image_equal(img_path, img_filelike)
    _clean()


def test_render_multiline():
    im = Image.new(mode='RGB', size=(300,100))
    draw = ImageDraw.Draw(im)
    ttf = ImageFont.truetype(font_path, font_size)
    line_spacing = draw.textsize('A', font=ttf)[1] + 8
    lines = ['hey you', 'you are awesome', 'this looks awkward']
    y = 0
    for line in lines:
        draw.text((0, y), line, font=ttf)
        y += line_spacing


    target = 'Tests/images/multiline_text.png'
    target_img = Image.open(target)
	
	# some versions of freetype have different horizontal spacing.
	# setting a tight epsilon, I'm showing the original test failure
	# at epsilon = ~38.
    assert_image_similar(im, target_img,.5)


def test_rotated_transposed_font():
    img_grey = Image.new("L", (100, 100))
    draw = ImageDraw.Draw(img_grey)
    word = "testing"
    font = ImageFont.truetype(font_path, font_size)

    orientation = Image.ROTATE_90
    transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

    # Original font
    draw.setfont(font)
    box_size_a = draw.textsize(word)

    # Rotated font
    draw.setfont(transposed_font)
    box_size_b = draw.textsize(word)

    # Check (w,h) of box a is (h,w) of box b
    assert_equal(box_size_a[0], box_size_b[1])
    assert_equal(box_size_a[1], box_size_b[0])


def test_unrotated_transposed_font():
    img_grey = Image.new("L", (100, 100))
    draw = ImageDraw.Draw(img_grey)
    word = "testing"
    font = ImageFont.truetype(font_path, font_size)

    orientation = None
    transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

    # Original font
    draw.setfont(font)
    box_size_a = draw.textsize(word)

    # Rotated font
    draw.setfont(transposed_font)
    box_size_b = draw.textsize(word)

    # Check boxes a and b are same size
    assert_equal(box_size_a, box_size_b)


