import copy
import os
import re
import shutil
import sys
from io import BytesIO

import pytest
from packaging.version import parse as parse_version

from PIL import Image, ImageDraw, ImageFont, features

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar_tofile,
    is_win32,
    skip_unless_feature,
    skip_unless_feature_version,
)

FONT_PATH = "Tests/fonts/FreeMono.ttf"
FONT_SIZE = 20

TEST_TEXT = "hey you\nyou are awesome\nthis looks awkward"


pytestmark = skip_unless_feature("freetype2")


def test_sanity():
    assert re.search(r"\d+\.\d+\.\d+$", features.version_module("freetype2"))


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(ImageFont.Layout.BASIC),
        pytest.param(ImageFont.Layout.RAQM, marks=skip_unless_feature("raqm")),
    ],
)
def layout_engine(request):
    return request.param


@pytest.fixture(scope="module")
def font(layout_engine):
    return ImageFont.truetype(FONT_PATH, FONT_SIZE, layout_engine=layout_engine)


def test_font_properties(font):
    assert font.path == FONT_PATH
    assert font.size == FONT_SIZE

    font_copy = font.font_variant()
    assert font_copy.path == FONT_PATH
    assert font_copy.size == FONT_SIZE

    font_copy = font.font_variant(size=FONT_SIZE + 1)
    assert font_copy.size == FONT_SIZE + 1

    second_font_path = "Tests/fonts/DejaVuSans/DejaVuSans.ttf"
    font_copy = font.font_variant(font=second_font_path)
    assert font_copy.path == second_font_path


def _render(font, layout_engine):
    txt = "Hello World!"
    ttf = ImageFont.truetype(font, FONT_SIZE, layout_engine=layout_engine)
    ttf.getbbox(txt)

    img = Image.new("RGB", (256, 64), "white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), txt, font=ttf, fill="black")

    return img


def test_font_with_name(layout_engine):
    _render(FONT_PATH, layout_engine)


def test_font_with_filelike(layout_engine):
    def _font_as_bytes():
        with open(FONT_PATH, "rb") as f:
            font_bytes = BytesIO(f.read())
        return font_bytes

    ttf = ImageFont.truetype(_font_as_bytes(), FONT_SIZE, layout_engine=layout_engine)
    ttf_copy = ttf.font_variant()
    assert ttf_copy.font_bytes == ttf.font_bytes

    _render(_font_as_bytes(), layout_engine)
    # Usage note:  making two fonts from the same buffer fails.
    # shared_bytes = _font_as_bytes()
    # _render(shared_bytes)
    # with pytest.raises(Exception):
    #   _render(shared_bytes)


def test_font_with_open_file(layout_engine):
    with open(FONT_PATH, "rb") as f:
        _render(f, layout_engine)


def test_render_equal(layout_engine):
    img_path = _render(FONT_PATH, layout_engine)
    with open(FONT_PATH, "rb") as f:
        font_filelike = BytesIO(f.read())
    img_filelike = _render(font_filelike, layout_engine)

    assert_image_equal(img_path, img_filelike)


def test_non_ascii_path(tmp_path, layout_engine):
    tempfile = str(tmp_path / ("temp_" + chr(128) + ".ttf"))
    try:
        shutil.copy(FONT_PATH, tempfile)
    except UnicodeEncodeError:
        pytest.skip("Non-ASCII path could not be created")

    ImageFont.truetype(tempfile, FONT_SIZE, layout_engine=layout_engine)


def test_transparent_background(font):
    im = Image.new(mode="RGBA", size=(300, 100))
    draw = ImageDraw.Draw(im)

    txt = "Hello World!"
    draw.text((10, 10), txt, font=font)

    target = "Tests/images/transparent_background_text.png"
    assert_image_similar_tofile(im, target, 4.09)

    target = "Tests/images/transparent_background_text_L.png"
    assert_image_similar_tofile(im.convert("L"), target, 0.01)


def test_I16(font):
    im = Image.new(mode="I;16", size=(300, 100))
    draw = ImageDraw.Draw(im)

    txt = "Hello World!"
    draw.text((10, 10), txt, font=font)

    target = "Tests/images/transparent_background_text_L.png"
    assert_image_similar_tofile(im.convert("L"), target, 0.01)


def test_textbbox_equal(font):
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    txt = "Hello World!"
    bbox = draw.textbbox((10, 10), txt, font)
    draw.text((10, 10), txt, font=font)
    draw.rectangle(bbox)

    assert_image_similar_tofile(im, "Tests/images/rectangle_surrounding_text.png", 2.5)


@pytest.mark.parametrize(
    "text, mode, fontname, size, length_basic, length_raqm",
    (
        # basic test
        ("text", "L", "FreeMono.ttf", 15, 36, 36),
        ("text", "1", "FreeMono.ttf", 15, 36, 36),
        # issue 4177
        ("rrr", "L", "DejaVuSans/DejaVuSans.ttf", 18, 21, 22.21875),
        ("rrr", "1", "DejaVuSans/DejaVuSans.ttf", 18, 24, 22.21875),
        # test 'l' not including extra margin
        # using exact value 2047 / 64 for raqm, checked with debugger
        ("ill", "L", "OpenSansCondensed-LightItalic.ttf", 63, 33, 31.984375),
        ("ill", "1", "OpenSansCondensed-LightItalic.ttf", 63, 33, 31.984375),
    ),
)
def test_getlength(
    text, mode, fontname, size, layout_engine, length_basic, length_raqm
):
    f = ImageFont.truetype("Tests/fonts/" + fontname, size, layout_engine=layout_engine)

    im = Image.new(mode, (1, 1), 0)
    d = ImageDraw.Draw(im)

    if layout_engine == ImageFont.Layout.BASIC:
        length = d.textlength(text, f)
        assert length == length_basic
    else:
        # disable kerning, kerning metrics changed
        length = d.textlength(text, f, features=["-kern"])
        assert length == length_raqm


def test_float_size():
    lengths = []
    for size in (48, 48.5, 49):
        f = ImageFont.truetype(
            "Tests/fonts/NotoSans-Regular.ttf", size, layout_engine=layout_engine
        )
        lengths.append(f.getlength("text"))
    assert lengths[0] != lengths[1] != lengths[2]


def test_render_multiline(font):
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    line_spacing = font.getbbox("A")[3] + 4
    lines = TEST_TEXT.split("\n")
    y = 0
    for line in lines:
        draw.text((0, y), line, font=font)
        y += line_spacing

    # some versions of freetype have different horizontal spacing.
    # setting a tight epsilon, I'm showing the original test failure
    # at epsilon = ~38.
    assert_image_similar_tofile(im, "Tests/images/multiline_text.png", 6.2)


def test_render_multiline_text(font):
    # Test that text() correctly connects to multiline_text()
    # and that align defaults to left
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), TEST_TEXT, font=font)

    assert_image_similar_tofile(im, "Tests/images/multiline_text.png", 0.01)

    # Test that text() can pass on additional arguments
    # to multiline_text()
    draw.text(
        (0, 0), TEST_TEXT, fill=None, font=font, anchor=None, spacing=4, align="left"
    )
    draw.text((0, 0), TEST_TEXT, None, font, None, 4, "left")


@pytest.mark.parametrize(
    "align, ext", (("left", ""), ("center", "_center"), ("right", "_right"))
)
def test_render_multiline_text_align(font, align, ext):
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.multiline_text((0, 0), TEST_TEXT, font=font, align=align)

    assert_image_similar_tofile(im, f"Tests/images/multiline_text{ext}.png", 0.01)


def test_unknown_align(font):
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Act/Assert
    with pytest.raises(ValueError):
        draw.multiline_text((0, 0), TEST_TEXT, font=font, align="unknown")


def test_draw_align(font):
    im = Image.new("RGB", (300, 100), "white")
    draw = ImageDraw.Draw(im)
    line = "some text"
    draw.text((100, 40), line, (0, 0, 0), font=font, align="left")


def test_multiline_bbox(font):
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Test that textbbox() correctly connects to multiline_textbbox()
    assert draw.textbbox((0, 0), TEST_TEXT, font=font) == draw.multiline_textbbox(
        (0, 0), TEST_TEXT, font=font
    )

    # Test that multiline_textbbox corresponds to ImageFont.textbbox()
    # for single line text
    assert font.getbbox("A") == draw.multiline_textbbox((0, 0), "A", font=font)

    # Test that textbbox() can pass on additional arguments
    # to multiline_textbbox()
    draw.textbbox((0, 0), TEST_TEXT, font=font, spacing=4)


def test_multiline_width(font):
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    assert (
        draw.textbbox((0, 0), "longest line", font=font)[2]
        == draw.multiline_textbbox((0, 0), "longest line\nline", font=font)[2]
    )


def test_multiline_spacing(font):
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.multiline_text((0, 0), TEST_TEXT, font=font, spacing=10)

    assert_image_similar_tofile(im, "Tests/images/multiline_text_spacing.png", 2.5)


@pytest.mark.parametrize(
    "orientation", (Image.Transpose.ROTATE_90, Image.Transpose.ROTATE_270)
)
def test_rotated_transposed_font(font, orientation):
    img_grey = Image.new("L", (100, 100))
    draw = ImageDraw.Draw(img_grey)
    word = "testing"

    transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

    # Original font
    draw.font = font
    bbox_a = draw.textbbox((10, 10), word)

    # Rotated font
    draw.font = transposed_font
    bbox_b = draw.textbbox((20, 20), word)

    # Check (w, h) of box a is (h, w) of box b
    assert (
        bbox_a[2] - bbox_a[0],
        bbox_a[3] - bbox_a[1],
    ) == (
        bbox_b[3] - bbox_b[1],
        bbox_b[2] - bbox_b[0],
    )

    # Check top left co-ordinates are correct
    assert bbox_b[:2] == (20, 20)

    # text length is undefined for vertical text
    with pytest.raises(ValueError):
        draw.textlength(word)


@pytest.mark.parametrize(
    "orientation",
    (
        None,
        Image.Transpose.ROTATE_180,
        Image.Transpose.FLIP_LEFT_RIGHT,
        Image.Transpose.FLIP_TOP_BOTTOM,
    ),
)
def test_unrotated_transposed_font(font, orientation):
    img_grey = Image.new("L", (100, 100))
    draw = ImageDraw.Draw(img_grey)
    word = "testing"

    transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

    # Original font
    draw.font = font
    bbox_a = draw.textbbox((10, 10), word)
    length_a = draw.textlength(word)

    # Rotated font
    draw.font = transposed_font
    bbox_b = draw.textbbox((20, 20), word)
    length_b = draw.textlength(word)

    # Check boxes a and b are same size
    assert (
        bbox_a[2] - bbox_a[0],
        bbox_a[3] - bbox_a[1],
    ) == (
        bbox_b[2] - bbox_b[0],
        bbox_b[3] - bbox_b[1],
    )

    # Check top left co-ordinates are correct
    assert bbox_b[:2] == (20, 20)

    assert length_a == length_b


@pytest.mark.parametrize(
    "orientation", (Image.Transpose.ROTATE_90, Image.Transpose.ROTATE_270)
)
def test_rotated_transposed_font_get_mask(font, orientation):
    # Arrange
    text = "mask this"
    transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

    # Act
    mask = transposed_font.getmask(text)

    # Assert
    assert mask.size == (13, 108)


@pytest.mark.parametrize(
    "orientation",
    (
        None,
        Image.Transpose.ROTATE_180,
        Image.Transpose.FLIP_LEFT_RIGHT,
        Image.Transpose.FLIP_TOP_BOTTOM,
    ),
)
def test_unrotated_transposed_font_get_mask(font, orientation):
    # Arrange
    text = "mask this"
    transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

    # Act
    mask = transposed_font.getmask(text)

    # Assert
    assert mask.size == (108, 13)


def test_free_type_font_get_name(font):
    assert ("FreeMono", "Regular") == font.getname()


def test_free_type_font_get_metrics(font):
    ascent, descent = font.getmetrics()

    assert isinstance(ascent, int)
    assert isinstance(descent, int)
    assert (ascent, descent) == (16, 4)


def test_free_type_font_get_mask(font):
    # Arrange
    text = "mask this"

    # Act
    mask = font.getmask(text)

    # Assert
    assert mask.size == (108, 13)


def test_load_path_not_found():
    # Arrange
    filename = "somefilenamethatdoesntexist.ttf"

    # Act/Assert
    with pytest.raises(OSError):
        ImageFont.load_path(filename)
    with pytest.raises(OSError):
        ImageFont.truetype(filename)


def test_load_non_font_bytes():
    with open("Tests/images/hopper.jpg", "rb") as f:
        with pytest.raises(OSError):
            ImageFont.truetype(f)


def test_default_font():
    # Arrange
    txt = 'This is a "better than nothing" default font.'
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Act
    default_font = ImageFont.load_default()
    draw.text((10, 10), txt, font=default_font)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/default_font.png")


@pytest.mark.parametrize("mode", (None, "1", "RGBA"))
def test_getbbox(font, mode):
    assert (0, 4, 12, 16) == font.getbbox("A", mode)


def test_getbbox_empty(font):
    # issue #2614, should not crash.
    assert (0, 0, 0, 0) == font.getbbox("")


def test_render_empty(font):
    # issue 2666
    im = Image.new(mode="RGB", size=(300, 100))
    target = im.copy()
    draw = ImageDraw.Draw(im)
    # should not crash here.
    draw.text((10, 10), "", font=font)
    assert_image_equal(im, target)


def test_unicode_pilfont():
    # should not segfault, should return UnicodeDecodeError
    # issue #2826
    font = ImageFont.load_default()
    with pytest.raises(UnicodeEncodeError):
        font.getbbox("’")


def test_unicode_extended(layout_engine):
    # issue #3777
    text = "A\u278A\U0001F12B"
    target = "Tests/images/unicode_extended.png"

    ttf = ImageFont.truetype(
        "Tests/fonts/NotoSansSymbols-Regular.ttf",
        FONT_SIZE,
        layout_engine=layout_engine,
    )
    img = Image.new("RGB", (100, 60))
    d = ImageDraw.Draw(img)
    d.text((10, 10), text, font=ttf)

    # fails with 14.7
    assert_image_similar_tofile(img, target, 6.2)


@pytest.mark.parametrize(
    "platform, font_directory",
    (("linux", "/usr/local/share/fonts"), ("darwin", "/System/Library/Fonts")),
)
@pytest.mark.skipif(is_win32(), reason="requires Unix or macOS")
def test_find_font(monkeypatch, platform, font_directory):
    def _test_fake_loading_font(path_to_fake, fontname):
        # Make a copy of FreeTypeFont so we can patch the original
        free_type_font = copy.deepcopy(ImageFont.FreeTypeFont)
        with monkeypatch.context() as m:
            m.setattr(ImageFont, "_FreeTypeFont", free_type_font, raising=False)

            def loadable_font(filepath, size, index, encoding, *args, **kwargs):
                if filepath == path_to_fake:
                    return ImageFont._FreeTypeFont(
                        FONT_PATH, size, index, encoding, *args, **kwargs
                    )
                return ImageFont._FreeTypeFont(
                    filepath, size, index, encoding, *args, **kwargs
                )

            m.setattr(ImageFont, "FreeTypeFont", loadable_font)
            font = ImageFont.truetype(fontname)
            # Make sure it's loaded
            name = font.getname()
            assert ("FreeMono", "Regular") == name

    # A lot of mocking here - this is more for hitting code and
    # catching syntax like errors
    monkeypatch.setattr(sys, "platform", platform)
    if platform == "linux":
        monkeypatch.setenv("XDG_DATA_DIRS", "/usr/share/:/usr/local/share/")

    def fake_walker(path):
        if path == font_directory:
            return [
                (
                    path,
                    [],
                    ["Arial.ttf", "Single.otf", "Duplicate.otf", "Duplicate.ttf"],
                )
            ]
        return [(path, [], ["some_random_font.ttf"])]

    monkeypatch.setattr(os, "walk", fake_walker)

    # Test that the font loads both with and without the extension
    _test_fake_loading_font(font_directory + "/Arial.ttf", "Arial.ttf")
    _test_fake_loading_font(font_directory + "/Arial.ttf", "Arial")

    # Test that non-ttf fonts can be found without the extension
    _test_fake_loading_font(font_directory + "/Single.otf", "Single")

    # Test that ttf fonts are preferred if the extension is not specified
    _test_fake_loading_font(font_directory + "/Duplicate.ttf", "Duplicate")


def test_imagefont_getters(font):
    assert font.getmetrics() == (16, 4)
    assert font.font.ascent == 16
    assert font.font.descent == 4
    assert font.font.height == 20
    assert font.font.x_ppem == 20
    assert font.font.y_ppem == 20
    assert font.font.glyphs == 4177
    assert font.getbbox("A") == (0, 4, 12, 16)
    assert font.getbbox("AB") == (0, 4, 24, 16)
    assert font.getbbox("M") == (0, 4, 12, 16)
    assert font.getbbox("y") == (0, 7, 12, 20)
    assert font.getbbox("a") == (0, 7, 12, 16)
    assert font.getlength("A") == 12
    assert font.getlength("AB") == 24
    assert font.getlength("M") == 12
    assert font.getlength("y") == 12
    assert font.getlength("a") == 12


@pytest.mark.parametrize("stroke_width", (0, 2))
def test_getsize_stroke(font, stroke_width):
    assert font.getbbox("A", stroke_width=stroke_width) == (
        0 - stroke_width,
        4 - stroke_width,
        12 + stroke_width,
        16 + stroke_width,
    )


def test_complex_font_settings():
    t = ImageFont.truetype(FONT_PATH, FONT_SIZE, layout_engine=ImageFont.Layout.BASIC)
    with pytest.raises(KeyError):
        t.getmask("абвг", direction="rtl")
    with pytest.raises(KeyError):
        t.getmask("абвг", features=["-kern"])
    with pytest.raises(KeyError):
        t.getmask("абвг", language="sr")


def test_variation_get(font):
    freetype = parse_version(features.version_module("freetype2"))
    if freetype < parse_version("2.9.1"):
        with pytest.raises(NotImplementedError):
            font.get_variation_names()
        with pytest.raises(NotImplementedError):
            font.get_variation_axes()
        return

    with pytest.raises(OSError):
        font.get_variation_names()
    with pytest.raises(OSError):
        font.get_variation_axes()

    font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf")
    assert font.get_variation_names(), [
        b"ExtraLight",
        b"Light",
        b"Regular",
        b"Semibold",
        b"Bold",
        b"Black",
        b"Black Medium Contrast",
        b"Black High Contrast",
        b"Default",
    ]
    assert font.get_variation_axes() == [
        {"name": b"Weight", "minimum": 200, "maximum": 900, "default": 389},
        {"name": b"Contrast", "minimum": 0, "maximum": 100, "default": 0},
    ]

    font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf")
    assert font.get_variation_names() == [
        b"20",
        b"40",
        b"60",
        b"80",
        b"100",
        b"120",
        b"140",
        b"160",
        b"180",
        b"200",
        b"220",
        b"240",
        b"260",
        b"280",
        b"300",
        b"Regular",
    ]
    assert font.get_variation_axes() == [
        {"name": b"Size", "minimum": 0, "maximum": 300, "default": 0}
    ]


def _check_text(font, path, epsilon):
    im = Image.new("RGB", (100, 75), "white")
    d = ImageDraw.Draw(im)
    d.text((10, 10), "Text", font=font, fill="black")

    try:
        assert_image_similar_tofile(im, path, epsilon)
    except AssertionError:
        if "_adobe" in path:
            path = path.replace("_adobe", "_adobe_older_harfbuzz")
            assert_image_similar_tofile(im, path, epsilon)
        else:
            raise


def test_variation_set_by_name(font):
    freetype = parse_version(features.version_module("freetype2"))
    if freetype < parse_version("2.9.1"):
        with pytest.raises(NotImplementedError):
            font.set_variation_by_name("Bold")
        return

    with pytest.raises(OSError):
        font.set_variation_by_name("Bold")

    font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf", 36)
    _check_text(font, "Tests/images/variation_adobe.png", 11)
    for name in ["Bold", b"Bold"]:
        font.set_variation_by_name(name)
        assert font.getname()[1] == "Bold"
    _check_text(font, "Tests/images/variation_adobe_name.png", 16)

    font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf", 36)
    _check_text(font, "Tests/images/variation_tiny.png", 40)
    for name in ["200", b"200"]:
        font.set_variation_by_name(name)
        assert font.getname()[1] == "200"
    _check_text(font, "Tests/images/variation_tiny_name.png", 40)


def test_variation_set_by_axes(font):
    freetype = parse_version(features.version_module("freetype2"))
    if freetype < parse_version("2.9.1"):
        with pytest.raises(NotImplementedError):
            font.set_variation_by_axes([100])
        return

    with pytest.raises(OSError):
        font.set_variation_by_axes([500, 50])

    font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf", 36)
    font.set_variation_by_axes([500, 50])
    _check_text(font, "Tests/images/variation_adobe_axes.png", 11.05)

    font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf", 36)
    font.set_variation_by_axes([100])
    _check_text(font, "Tests/images/variation_tiny_axes.png", 32.5)


def test_textbbox_non_freetypefont():
    im = Image.new("RGB", (200, 200))
    d = ImageDraw.Draw(im)
    default_font = ImageFont.load_default()
    assert d.textlength("test", font=default_font) == 24
    assert d.textbbox((0, 0), "test", font=default_font) == (0, 0, 24, 11)


@pytest.mark.parametrize(
    "anchor, left, top",
    (
        # test horizontal anchors
        ("ls", 0, -36),
        ("ms", -64, -36),
        ("rs", -128, -36),
        # test vertical anchors
        ("ma", -64, 16),
        ("mt", -64, 0),
        ("mm", -64, -17),
        ("mb", -64, -44),
        ("md", -64, -51),
    ),
    ids=("ls", "ms", "rs", "ma", "mt", "mm", "mb", "md"),
)
def test_anchor(layout_engine, anchor, left, top):
    name, text = "quick", "Quick"
    path = f"Tests/images/test_anchor_{name}_{anchor}.png"

    if layout_engine == ImageFont.Layout.RAQM:
        width, height = (129, 44)
    else:
        width, height = (128, 44)

    bbox_expected = (left, top, left + width, top + height)

    f = ImageFont.truetype(
        "Tests/fonts/NotoSans-Regular.ttf", 48, layout_engine=layout_engine
    )

    im = Image.new("RGB", (200, 200), "white")
    d = ImageDraw.Draw(im)
    d.line(((0, 100), (200, 100)), "gray")
    d.line(((100, 0), (100, 200)), "gray")
    d.text((100, 100), text, fill="black", anchor=anchor, font=f)

    assert d.textbbox((0, 0), text, f, anchor=anchor) == bbox_expected

    assert_image_similar_tofile(im, path, 7)


@pytest.mark.parametrize(
    "anchor, align",
    (
        # test horizontal anchors
        ("lm", "left"),
        ("lm", "center"),
        ("lm", "right"),
        ("mm", "left"),
        ("mm", "center"),
        ("mm", "right"),
        ("rm", "left"),
        ("rm", "center"),
        ("rm", "right"),
        # test vertical anchors
        ("ma", "center"),
        # ("mm", "center"),  # duplicate
        ("md", "center"),
    ),
)
def test_anchor_multiline(layout_engine, anchor, align):
    target = f"Tests/images/test_anchor_multiline_{anchor}_{align}.png"
    text = "a\nlong\ntext sample"

    f = ImageFont.truetype(
        "Tests/fonts/NotoSans-Regular.ttf", 48, layout_engine=layout_engine
    )

    # test render
    im = Image.new("RGB", (600, 400), "white")
    d = ImageDraw.Draw(im)
    d.line(((0, 200), (600, 200)), "gray")
    d.line(((300, 0), (300, 400)), "gray")
    d.multiline_text((300, 200), text, fill="black", anchor=anchor, font=f, align=align)

    assert_image_similar_tofile(im, target, 4)


def test_anchor_invalid(font):
    im = Image.new("RGB", (100, 100), "white")
    d = ImageDraw.Draw(im)
    d.font = font

    for anchor in ["", "l", "a", "lax", "sa", "xa", "lx"]:
        with pytest.raises(ValueError):
            font.getmask2("hello", anchor=anchor)
        with pytest.raises(ValueError):
            font.getbbox("hello", anchor=anchor)
        with pytest.raises(ValueError):
            d.text((0, 0), "hello", anchor=anchor)
        with pytest.raises(ValueError):
            d.textbbox((0, 0), "hello", anchor=anchor)
        with pytest.raises(ValueError):
            d.multiline_text((0, 0), "foo\nbar", anchor=anchor)
        with pytest.raises(ValueError):
            d.multiline_textbbox((0, 0), "foo\nbar", anchor=anchor)
    for anchor in ["lt", "lb"]:
        with pytest.raises(ValueError):
            d.multiline_text((0, 0), "foo\nbar", anchor=anchor)
        with pytest.raises(ValueError):
            d.multiline_textbbox((0, 0), "foo\nbar", anchor=anchor)


@pytest.mark.parametrize("bpp", (1, 2, 4, 8))
def test_bitmap_font(layout_engine, bpp):
    text = "Bitmap Font"
    layout_name = ["basic", "raqm"][layout_engine]
    target = f"Tests/images/bitmap_font_{bpp}_{layout_name}.png"
    font = ImageFont.truetype(
        f"Tests/fonts/DejaVuSans/DejaVuSans-24-{bpp}-stripped.ttf",
        24,
        layout_engine=layout_engine,
    )

    im = Image.new("RGB", (160, 35), "white")
    draw = ImageDraw.Draw(im)
    draw.text((2, 2), text, "black", font)

    assert_image_equal_tofile(im, target)


def test_bitmap_font_stroke(layout_engine):
    text = "Bitmap Font"
    layout_name = ["basic", "raqm"][layout_engine]
    target = f"Tests/images/bitmap_font_stroke_{layout_name}.png"
    font = ImageFont.truetype(
        "Tests/fonts/DejaVuSans/DejaVuSans-24-8-stripped.ttf",
        24,
        layout_engine=layout_engine,
    )

    im = Image.new("RGB", (160, 35), "white")
    draw = ImageDraw.Draw(im)
    draw.text((2, 2), text, "black", font, stroke_width=2, stroke_fill="red")

    assert_image_similar_tofile(im, target, 0.03)


def test_standard_embedded_color(layout_engine):
    txt = "Hello World!"
    ttf = ImageFont.truetype(FONT_PATH, 40, layout_engine=layout_engine)
    ttf.getbbox(txt)

    im = Image.new("RGB", (300, 64), "white")
    d = ImageDraw.Draw(im)
    d.text((10, 10), txt, font=ttf, fill="#fa6", embedded_color=True)

    assert_image_similar_tofile(im, "Tests/images/standard_embedded.png", 3.1)


@pytest.mark.parametrize("fontmode", ("1", "L", "RGBA"))
def test_float_coord(layout_engine, fontmode):
    txt = "Hello World!"
    ttf = ImageFont.truetype(FONT_PATH, 40, layout_engine=layout_engine)

    im = Image.new("RGB", (300, 64), "white")
    d = ImageDraw.Draw(im)
    if fontmode == "1":
        d.fontmode = "1"

    embedded_color = fontmode == "RGBA"
    d.text((9.5, 9.5), txt, font=ttf, fill="#fa6", embedded_color=embedded_color)
    try:
        assert_image_similar_tofile(im, "Tests/images/text_float_coord.png", 3.9)
    except AssertionError:
        if fontmode == "1" and layout_engine == ImageFont.Layout.BASIC:
            assert_image_similar_tofile(
                im, "Tests/images/text_float_coord_1_alt.png", 1
            )
        else:
            raise


def test_cbdt(layout_engine):
    try:
        font = ImageFont.truetype(
            "Tests/fonts/NotoColorEmoji.ttf", size=109, layout_engine=layout_engine
        )

        im = Image.new("RGB", (150, 150), "white")
        d = ImageDraw.Draw(im)

        d.text((10, 10), "\U0001f469", font=font, embedded_color=True)

        assert_image_similar_tofile(im, "Tests/images/cbdt_notocoloremoji.png", 6.2)
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or CBDT support")


def test_cbdt_mask(layout_engine):
    try:
        font = ImageFont.truetype(
            "Tests/fonts/NotoColorEmoji.ttf", size=109, layout_engine=layout_engine
        )

        im = Image.new("RGB", (150, 150), "white")
        d = ImageDraw.Draw(im)

        d.text((10, 10), "\U0001f469", "black", font=font)

        assert_image_similar_tofile(
            im, "Tests/images/cbdt_notocoloremoji_mask.png", 6.2
        )
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or CBDT support")


def test_sbix(layout_engine):
    try:
        font = ImageFont.truetype(
            "Tests/fonts/chromacheck-sbix.woff", size=300, layout_engine=layout_engine
        )

        im = Image.new("RGB", (400, 400), "white")
        d = ImageDraw.Draw(im)

        d.text((50, 50), "\uE901", font=font, embedded_color=True)

        assert_image_similar_tofile(im, "Tests/images/chromacheck-sbix.png", 1)
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or SBIX support")


def test_sbix_mask(layout_engine):
    try:
        font = ImageFont.truetype(
            "Tests/fonts/chromacheck-sbix.woff", size=300, layout_engine=layout_engine
        )

        im = Image.new("RGB", (400, 400), "white")
        d = ImageDraw.Draw(im)

        d.text((50, 50), "\uE901", (100, 0, 0), font=font)

        assert_image_similar_tofile(im, "Tests/images/chromacheck-sbix_mask.png", 1)
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or SBIX support")


@skip_unless_feature_version("freetype2", "2.10.0")
def test_colr(layout_engine):
    font = ImageFont.truetype(
        "Tests/fonts/BungeeColor-Regular_colr_Windows.ttf",
        size=64,
        layout_engine=layout_engine,
    )

    im = Image.new("RGB", (300, 75), "white")
    d = ImageDraw.Draw(im)

    d.text((15, 5), "Bungee", font=font, embedded_color=True)

    assert_image_similar_tofile(im, "Tests/images/colr_bungee.png", 21)


@skip_unless_feature_version("freetype2", "2.10.0")
def test_colr_mask(layout_engine):
    font = ImageFont.truetype(
        "Tests/fonts/BungeeColor-Regular_colr_Windows.ttf",
        size=64,
        layout_engine=layout_engine,
    )

    im = Image.new("RGB", (300, 75), "white")
    d = ImageDraw.Draw(im)

    d.text((15, 5), "Bungee", "black", font=font)

    assert_image_similar_tofile(im, "Tests/images/colr_bungee_mask.png", 22)


def test_woff2(layout_engine):
    try:
        font = ImageFont.truetype(
            "Tests/fonts/OpenSans.woff2",
            size=64,
            layout_engine=layout_engine,
        )
    except OSError as e:
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("FreeType compiled without brotli or WOFF2 support")

    im = Image.new("RGB", (350, 100), "white")
    d = ImageDraw.Draw(im)

    d.text((15, 5), "OpenSans", "black", font=font)

    assert_image_similar_tofile(im, "Tests/images/test_woff2.png", 5)


def test_render_mono_size():
    # issue 4177

    im = Image.new("P", (100, 30), "white")
    draw = ImageDraw.Draw(im)
    ttf = ImageFont.truetype(
        "Tests/fonts/DejaVuSans/DejaVuSans.ttf",
        18,
        layout_engine=ImageFont.Layout.BASIC,
    )

    draw.text((10, 10), "r" * 10, "black", ttf)
    assert_image_equal_tofile(im, "Tests/images/text_mono.gif")


def test_too_many_characters(font):
    with pytest.raises(ValueError):
        font.getlength("A" * 1_000_001)
    with pytest.raises(ValueError):
        font.getbbox("A" * 1_000_001)
    with pytest.raises(ValueError):
        font.getmask2("A" * 1_000_001)

    transposed_font = ImageFont.TransposedFont(font)
    with pytest.raises(ValueError):
        transposed_font.getlength("A" * 1_000_001)

    default_font = ImageFont.load_default()
    with pytest.raises(ValueError):
        default_font.getlength("A" * 1_000_001)
    with pytest.raises(ValueError):
        default_font.getbbox("A" * 1_000_001)


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/fonts/oom-e8e927ba6c0d38274a37c1567560eb33baf74627.ttf",
        "Tests/fonts/oom-4da0210eb7081b0bf15bf16cc4c52ce02c1e1bbc.ttf",
    ],
)
def test_oom(test_file):
    with open(test_file, "rb") as f:
        font = ImageFont.truetype(BytesIO(f.read()))
        with pytest.raises(Image.DecompressionBombError):
            font.getmask("Test Text")


def test_raqm_missing_warning(monkeypatch):
    monkeypatch.setattr(ImageFont.core, "HAVE_RAQM", False)
    with pytest.warns(UserWarning) as record:
        font = ImageFont.truetype(
            FONT_PATH, FONT_SIZE, layout_engine=ImageFont.Layout.RAQM
        )
    assert font.layout_engine == ImageFont.Layout.BASIC
    assert str(record[-1].message) == (
        "Raqm layout was requested, but Raqm is not available. "
        "Falling back to basic layout."
    )
