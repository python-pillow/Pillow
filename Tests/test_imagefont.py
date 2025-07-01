from __future__ import annotations

import copy
import os
import re
import shutil
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, BinaryIO

import pytest

from PIL import Image, ImageDraw, ImageFont, features
from PIL._typing import StrOrBytesPath

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


def test_sanity() -> None:
    version = features.version_module("freetype2")
    assert version is not None
    assert re.search(r"\d+\.\d+\.\d+$", version)


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(ImageFont.Layout.BASIC),
        pytest.param(ImageFont.Layout.RAQM, marks=skip_unless_feature("raqm")),
    ],
)
def layout_engine(request: pytest.FixtureRequest) -> ImageFont.Layout:
    return request.param


@pytest.fixture(scope="module")
def font(layout_engine: ImageFont.Layout) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, FONT_SIZE, layout_engine=layout_engine)


def test_font_properties(font: ImageFont.FreeTypeFont) -> None:
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


def _render(
    font: StrOrBytesPath | BinaryIO, layout_engine: ImageFont.Layout
) -> Image.Image:
    txt = "Hello World!"
    ttf = ImageFont.truetype(font, FONT_SIZE, layout_engine=layout_engine)
    ttf.getbbox(txt)

    img = Image.new("RGB", (256, 64), "white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), txt, font=ttf, fill="black")

    return img


@pytest.mark.parametrize("font", (FONT_PATH, Path(FONT_PATH)))
def test_font_with_name(layout_engine: ImageFont.Layout, font: str | Path) -> None:
    _render(font, layout_engine)


def test_font_with_filelike(layout_engine: ImageFont.Layout) -> None:
    def _font_as_bytes() -> BytesIO:
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


def test_font_with_open_file(layout_engine: ImageFont.Layout) -> None:
    with open(FONT_PATH, "rb") as f:
        _render(f, layout_engine)


def test_render_equal(layout_engine: ImageFont.Layout) -> None:
    img_path = _render(FONT_PATH, layout_engine)
    with open(FONT_PATH, "rb") as f:
        font_filelike = BytesIO(f.read())
    img_filelike = _render(font_filelike, layout_engine)

    assert_image_equal(img_path, img_filelike)


def test_non_ascii_path(tmp_path: Path, layout_engine: ImageFont.Layout) -> None:
    tempfile = tmp_path / ("temp_" + chr(128) + ".ttf")
    try:
        shutil.copy(FONT_PATH, tempfile)
    except UnicodeEncodeError:
        pytest.skip("Non-ASCII path could not be created")

    ImageFont.truetype(tempfile, FONT_SIZE, layout_engine=layout_engine)


def test_transparent_background(font: ImageFont.FreeTypeFont) -> None:
    im = Image.new(mode="RGBA", size=(300, 100))
    draw = ImageDraw.Draw(im)

    txt = "Hello World!"
    draw.text((10, 10), txt, font=font)

    target = "Tests/images/transparent_background_text.png"
    assert_image_similar_tofile(im, target, 4.09)

    target = "Tests/images/transparent_background_text_L.png"
    assert_image_similar_tofile(im.convert("L"), target, 0.01)


def test_I16(font: ImageFont.FreeTypeFont) -> None:
    im = Image.new(mode="I;16", size=(300, 100))
    draw = ImageDraw.Draw(im)

    txt = "Hello World!"
    draw.text((10, 10), txt, fill=0xFFFE, font=font)

    assert im.getpixel((12, 14)) == 0xFFFE

    target = "Tests/images/transparent_background_text_L.png"
    assert_image_similar_tofile(im.convert("L"), target, 0.01)


def test_textbbox_equal(font: ImageFont.FreeTypeFont) -> None:
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
    text: str,
    mode: str,
    fontname: str,
    size: int,
    layout_engine: ImageFont.Layout,
    length_basic: int,
    length_raqm: float,
) -> None:
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


def test_float_size(layout_engine: ImageFont.Layout) -> None:
    lengths = []
    for size in (48, 48.5, 49):
        f = ImageFont.truetype(
            "Tests/fonts/NotoSans-Regular.ttf", size, layout_engine=layout_engine
        )
        lengths.append(f.getlength("text"))
    assert lengths[0] != lengths[1] != lengths[2]


def test_render_multiline(font: ImageFont.FreeTypeFont) -> None:
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    line_spacing = font.getbbox("A")[3] + 4
    lines = TEST_TEXT.split("\n")
    y: float = 0
    for line in lines:
        draw.text((0, y), line, font=font)
        y += line_spacing

    # some versions of freetype have different horizontal spacing.
    # setting a tight epsilon, I'm showing the original test failure
    # at epsilon = ~38.
    assert_image_similar_tofile(im, "Tests/images/multiline_text.png", 6.2)


def test_render_multiline_text(font: ImageFont.FreeTypeFont) -> None:
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
    "align, ext",
    (("left", ""), ("center", "_center"), ("right", "_right"), ("justify", "_justify")),
)
def test_render_multiline_text_align(
    font: ImageFont.FreeTypeFont, align: str, ext: str
) -> None:
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.multiline_text((0, 0), TEST_TEXT, font=font, align=align)

    assert_image_similar_tofile(im, f"Tests/images/multiline_text{ext}.png", 0.01)


def test_render_multiline_text_justify_anchor(
    font: ImageFont.FreeTypeFont,
) -> None:
    im = Image.new("RGB", (280, 240))
    draw = ImageDraw.Draw(im)
    for xy, anchor in (((0, 0), "la"), ((140, 80), "ma"), ((280, 160), "ra")):
        draw.multiline_text(
            xy,
            "hey you you are awesome\nthis looks awkward\nthis\nlooks awkward",
            font=font,
            anchor=anchor,
            align="justify",
        )

    assert_image_equal_tofile(im, "Tests/images/multiline_text_justify_anchor.png")


def test_unknown_align(font: ImageFont.FreeTypeFont) -> None:
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Act/Assert
    with pytest.raises(ValueError):
        draw.multiline_text((0, 0), TEST_TEXT, font=font, align="unknown")


def test_draw_align(font: ImageFont.FreeTypeFont) -> None:
    im = Image.new("RGB", (300, 100), "white")
    draw = ImageDraw.Draw(im)
    line = "some text"
    draw.text((100, 40), line, (0, 0, 0), font=font, align="left")


def test_multiline_bbox(font: ImageFont.FreeTypeFont) -> None:
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


def test_multiline_width(font: ImageFont.FreeTypeFont) -> None:
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    assert (
        draw.textbbox((0, 0), "longest line", font=font)[2]
        == draw.multiline_textbbox((0, 0), "longest line\nline", font=font)[2]
    )


def test_multiline_spacing(font: ImageFont.FreeTypeFont) -> None:
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.multiline_text((0, 0), TEST_TEXT, font=font, spacing=10)

    assert_image_similar_tofile(im, "Tests/images/multiline_text_spacing.png", 2.5)


@pytest.mark.parametrize(
    "orientation", (Image.Transpose.ROTATE_90, Image.Transpose.ROTATE_270)
)
def test_rotated_transposed_font(
    font: ImageFont.FreeTypeFont, orientation: Image.Transpose
) -> None:
    img_gray = Image.new("L", (100, 100))
    draw = ImageDraw.Draw(img_gray)
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
def test_unrotated_transposed_font(
    font: ImageFont.FreeTypeFont, orientation: Image.Transpose
) -> None:
    img_gray = Image.new("L", (100, 100))
    draw = ImageDraw.Draw(img_gray)
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
def test_rotated_transposed_font_get_mask(
    font: ImageFont.FreeTypeFont, orientation: Image.Transpose
) -> None:
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
def test_unrotated_transposed_font_get_mask(
    font: ImageFont.FreeTypeFont, orientation: Image.Transpose
) -> None:
    # Arrange
    text = "mask this"
    transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

    # Act
    mask = transposed_font.getmask(text)

    # Assert
    assert mask.size == (108, 13)


def test_free_type_font_get_name(font: ImageFont.FreeTypeFont) -> None:
    assert ("FreeMono", "Regular") == font.getname()


def test_free_type_font_get_metrics(font: ImageFont.FreeTypeFont) -> None:
    ascent, descent = font.getmetrics()

    assert isinstance(ascent, int)
    assert isinstance(descent, int)
    assert (ascent, descent) == (16, 4)


def test_free_type_font_get_mask(font: ImageFont.FreeTypeFont) -> None:
    # Arrange
    text = "mask this"

    # Act
    mask = font.getmask(text)

    # Assert
    assert mask.size == (108, 13)


def test_stroke_mask() -> None:
    # Arrange
    text = "i"

    # Act
    font = ImageFont.truetype(FONT_PATH, 128)
    mask = font.getmask(text, stroke_width=2)

    # Assert
    assert mask.getpixel((34, 5)) == 255
    assert mask.getpixel((38, 5)) == 0
    assert mask.getpixel((42, 5)) == 255


def test_load_when_image_not_found() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        pass
    with pytest.raises(OSError) as e:
        ImageFont.load(tmp.name)

    os.unlink(tmp.name)

    root = os.path.splitext(tmp.name)[0]
    assert str(e.value) == f"cannot find glyph data file {root}.{{gif|pbm|png}}"


def test_load_path_not_found() -> None:
    # Arrange
    filename = "somefilenamethatdoesntexist.ttf"

    # Act/Assert
    with pytest.raises(OSError) as e:
        ImageFont.load_path(filename)

    # The file doesn't exist, so don't suggest `load`
    assert filename in str(e.value)
    assert "did you mean" not in str(e.value)
    with pytest.raises(OSError):
        ImageFont.truetype(filename)


def test_load_path_existing_path() -> None:
    with tempfile.NamedTemporaryFile() as tmp:
        with pytest.raises(OSError) as e:
            ImageFont.load_path(tmp.name)

    # The file exists, so the error message suggests to use `load` instead
    assert tmp.name in str(e.value)
    assert " did you mean" in str(e.value)


def test_load_non_font_bytes() -> None:
    with open("Tests/images/hopper.jpg", "rb") as f:
        with pytest.raises(OSError):
            ImageFont.truetype(f)


def test_default_font() -> None:
    # Arrange
    txt = "This is a default font using FreeType support."
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)

    # Act
    default_font = ImageFont.load_default()
    draw.text((10, 10), txt, font=default_font)

    larger_default_font = ImageFont.load_default(size=14)
    draw.text((10, 60), txt, font=larger_default_font)

    # Assert
    assert_image_equal_tofile(im, "Tests/images/default_font_freetype.png")


@pytest.mark.parametrize("mode", ("", "1", "RGBA"))
def test_getbbox(font: ImageFont.FreeTypeFont, mode: str) -> None:
    assert (0, 4, 12, 16) == font.getbbox("A", mode)


def test_getbbox_empty(font: ImageFont.FreeTypeFont) -> None:
    # issue #2614, should not crash.
    assert (0, 0, 0, 0) == font.getbbox("")


def test_render_empty(font: ImageFont.FreeTypeFont) -> None:
    # issue 2666
    im = Image.new(mode="RGB", size=(300, 100))
    target = im.copy()
    draw = ImageDraw.Draw(im)
    # should not crash here.
    draw.text((10, 10), "", font=font)
    assert_image_equal(im, target)


def test_unicode_extended(layout_engine: ImageFont.Layout) -> None:
    # issue #3777
    text = "A\u278a\U0001f12b"
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
def test_find_font(
    monkeypatch: pytest.MonkeyPatch, platform: str, font_directory: str
) -> None:
    def _test_fake_loading_font(path_to_fake: str, fontname: str) -> None:
        # Make a copy of FreeTypeFont so we can patch the original
        free_type_font = copy.deepcopy(ImageFont.FreeTypeFont)
        with monkeypatch.context() as m:
            m.setattr(ImageFont, "_FreeTypeFont", free_type_font, raising=False)

            def loadable_font(
                filepath: str, size: int, index: int, encoding: str, *args: Any
            ) -> ImageFont.FreeTypeFont:
                _freeTypeFont = getattr(ImageFont, "_FreeTypeFont")
                if filepath == path_to_fake:
                    return _freeTypeFont(FONT_PATH, size, index, encoding, *args)
                return _freeTypeFont(filepath, size, index, encoding, *args)

            m.setattr(ImageFont, "FreeTypeFont", loadable_font)
            font = ImageFont.truetype(fontname)
            # Make sure it's loaded
            name = font.getname()
            assert ("FreeMono", "Regular") == name

    # A lot of mocking here - this is more for hitting code and
    # catching syntax like errors
    monkeypatch.setattr(sys, "platform", platform)
    if platform == "linux":
        monkeypatch.setenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        monkeypatch.setenv("XDG_DATA_DIRS", "/usr/share/:/usr/local/share/")

    def fake_walker(path: str) -> list[tuple[str, list[str], list[str]]]:
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


def test_imagefont_getters(font: ImageFont.FreeTypeFont) -> None:
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
def test_getsize_stroke(font: ImageFont.FreeTypeFont, stroke_width: int) -> None:
    assert font.getbbox("A", stroke_width=stroke_width) == (
        0 - stroke_width,
        4 - stroke_width,
        12 + stroke_width,
        16 + stroke_width,
    )


def test_complex_font_settings() -> None:
    t = ImageFont.truetype(FONT_PATH, FONT_SIZE, layout_engine=ImageFont.Layout.BASIC)
    with pytest.raises(KeyError):
        t.getmask("абвг", direction="rtl")
    with pytest.raises(KeyError):
        t.getmask("абвг", features=["-kern"])
    with pytest.raises(KeyError):
        t.getmask("абвг", language="sr")


def test_variation_get(font: ImageFont.FreeTypeFont) -> None:
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


def _check_text(font: ImageFont.FreeTypeFont, path: str, epsilon: float) -> None:
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


def test_variation_set_by_name(font: ImageFont.FreeTypeFont) -> None:
    with pytest.raises(OSError):
        font.set_variation_by_name("Bold")

    font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf", 36)
    _check_text(font, "Tests/images/variation_adobe.png", 11)
    for name in ("Bold", b"Bold"):
        font.set_variation_by_name(name)
        assert font.getname()[1] == "Bold"
    _check_text(font, "Tests/images/variation_adobe_name.png", 16)

    font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf", 36)
    _check_text(font, "Tests/images/variation_tiny.png", 40)
    for name in ("200", b"200"):
        font.set_variation_by_name(name)
        assert font.getname()[1] == "200"
    _check_text(font, "Tests/images/variation_tiny_name.png", 40)


def test_variation_set_by_axes(font: ImageFont.FreeTypeFont) -> None:
    with pytest.raises(OSError):
        font.set_variation_by_axes([500, 50])

    font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf", 36)
    font.set_variation_by_axes([500, 50])
    _check_text(font, "Tests/images/variation_adobe_axes.png", 11.05)

    font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf", 36)
    font.set_variation_by_axes([100])
    _check_text(font, "Tests/images/variation_tiny_axes.png", 32.5)


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
def test_anchor(
    layout_engine: ImageFont.Layout, anchor: str, left: int, top: int
) -> None:
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
def test_anchor_multiline(
    layout_engine: ImageFont.Layout, anchor: str, align: str
) -> None:
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


def test_anchor_invalid(font: ImageFont.FreeTypeFont) -> None:
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
def test_bitmap_font(layout_engine: ImageFont.Layout, bpp: int) -> None:
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


def test_bitmap_font_stroke(layout_engine: ImageFont.Layout) -> None:
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


@pytest.mark.parametrize("embedded_color", (False, True))
def test_bitmap_blend(layout_engine: ImageFont.Layout, embedded_color: bool) -> None:
    font = ImageFont.truetype(
        "Tests/fonts/EBDTTestFont.ttf", size=64, layout_engine=layout_engine
    )

    im = Image.new("RGBA", (128, 96), "white")
    d = ImageDraw.Draw(im)
    d.text((16, 16), "AA", font=font, fill="#8E2F52", embedded_color=embedded_color)

    assert_image_equal_tofile(im, "Tests/images/bitmap_font_blend.png")


def test_standard_embedded_color(layout_engine: ImageFont.Layout) -> None:
    txt = "Hello World!"
    ttf = ImageFont.truetype(FONT_PATH, 40, layout_engine=layout_engine)
    ttf.getbbox(txt)

    im = Image.new("RGB", (300, 64), "white")
    d = ImageDraw.Draw(im)
    d.text((10, 10), txt, font=ttf, fill="#fa6", embedded_color=True)

    assert_image_similar_tofile(im, "Tests/images/standard_embedded.png", 3.1)


@pytest.mark.parametrize("fontmode", ("1", "L", "RGBA"))
def test_float_coord(layout_engine: ImageFont.Layout, fontmode: str) -> None:
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


def test_cbdt(layout_engine: ImageFont.Layout) -> None:
    try:
        font = ImageFont.truetype(
            "Tests/fonts/CBDTTestFont.ttf", size=64, layout_engine=layout_engine
        )

        im = Image.new("RGB", (128, 96), "white")
        d = ImageDraw.Draw(im)

        d.text((16, 16), "AB", font=font, embedded_color=True)

        assert_image_equal_tofile(im, "Tests/images/cbdt.png")
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or CBDT support")


def test_cbdt_mask(layout_engine: ImageFont.Layout) -> None:
    try:
        font = ImageFont.truetype(
            "Tests/fonts/CBDTTestFont.ttf", size=64, layout_engine=layout_engine
        )

        im = Image.new("RGB", (128, 96), "white")
        d = ImageDraw.Draw(im)

        d.text((16, 16), "AB", "green", font=font)

        assert_image_equal_tofile(im, "Tests/images/cbdt_mask.png")
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or CBDT support")


def test_sbix(layout_engine: ImageFont.Layout) -> None:
    try:
        font = ImageFont.truetype(
            "Tests/fonts/chromacheck-sbix.woff", size=300, layout_engine=layout_engine
        )

        im = Image.new("RGB", (400, 400), "white")
        d = ImageDraw.Draw(im)

        d.text((50, 50), "\ue901", font=font, embedded_color=True)

        assert_image_similar_tofile(im, "Tests/images/chromacheck-sbix.png", 1)
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or SBIX support")


def test_sbix_mask(layout_engine: ImageFont.Layout) -> None:
    try:
        font = ImageFont.truetype(
            "Tests/fonts/chromacheck-sbix.woff", size=300, layout_engine=layout_engine
        )

        im = Image.new("RGB", (400, 400), "white")
        d = ImageDraw.Draw(im)

        d.text((50, 50), "\ue901", (100, 0, 0), font=font)

        assert_image_similar_tofile(im, "Tests/images/chromacheck-sbix_mask.png", 1)
    except OSError as e:  # pragma: no cover
        assert str(e) in ("unimplemented feature", "unknown file format")
        pytest.skip("freetype compiled without libpng or SBIX support")


@skip_unless_feature_version("freetype2", "2.10.0")
def test_colr(layout_engine: ImageFont.Layout) -> None:
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
def test_colr_mask(layout_engine: ImageFont.Layout) -> None:
    font = ImageFont.truetype(
        "Tests/fonts/BungeeColor-Regular_colr_Windows.ttf",
        size=64,
        layout_engine=layout_engine,
    )

    im = Image.new("RGB", (300, 75), "white")
    d = ImageDraw.Draw(im)

    d.text((15, 5), "Bungee", "black", font=font)

    assert_image_similar_tofile(im, "Tests/images/colr_bungee_mask.png", 22)


def test_woff2(layout_engine: ImageFont.Layout) -> None:
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


def test_render_mono_size() -> None:
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


def test_too_many_characters(font: ImageFont.FreeTypeFont) -> None:
    with pytest.raises(ValueError):
        font.getlength("A" * 1_000_001)
    with pytest.raises(ValueError):
        font.getbbox("A" * 1_000_001)
    with pytest.raises(ValueError):
        font.getmask2("A" * 1_000_001)

    transposed_font = ImageFont.TransposedFont(font)
    with pytest.raises(ValueError):
        transposed_font.getlength("A" * 1_000_001)

    imagefont = ImageFont.ImageFont()
    with pytest.raises(ValueError):
        imagefont.getlength("A" * 1_000_001)
    with pytest.raises(ValueError):
        imagefont.getbbox("A" * 1_000_001)
    with pytest.raises(ValueError):
        imagefont.getmask("A" * 1_000_001)


def test_bytes(font: ImageFont.FreeTypeFont) -> None:
    assert font.getlength(b"test") == font.getlength("test")

    assert font.getbbox(b"test") == font.getbbox("test")

    assert_image_equal(
        Image.Image()._new(font.getmask(b"test")),
        Image.Image()._new(font.getmask("test")),
    )

    assert_image_equal(
        Image.Image()._new(font.getmask2(b"test")[0]),
        Image.Image()._new(font.getmask2("test")[0]),
    )
    assert font.getmask2(b"test")[1] == font.getmask2("test")[1]

    with pytest.raises(TypeError):
        font.getlength((0, 0))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/fonts/oom-e8e927ba6c0d38274a37c1567560eb33baf74627.ttf",
        "Tests/fonts/oom-4da0210eb7081b0bf15bf16cc4c52ce02c1e1bbc.ttf",
    ],
)
def test_oom(test_file: str) -> None:
    with open(test_file, "rb") as f:
        font = ImageFont.truetype(BytesIO(f.read()))
        with pytest.raises(Image.DecompressionBombError):
            font.getmask("Test Text")


def test_raqm_missing_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ImageFont.core, "HAVE_RAQM", False)
    with pytest.warns(
        UserWarning,
        match="Raqm layout was requested, but Raqm is not available. "
        "Falling back to basic layout.",
    ):
        font = ImageFont.truetype(
            FONT_PATH, FONT_SIZE, layout_engine=ImageFont.Layout.RAQM
        )
    assert font.layout_engine == ImageFont.Layout.BASIC


@pytest.mark.parametrize("size", [-1, 0])
def test_invalid_truetype_sizes_raise_valueerror(
    layout_engine: ImageFont.Layout, size: int
) -> None:
    with pytest.raises(ValueError):
        ImageFont.truetype(FONT_PATH, size, layout_engine=layout_engine)
