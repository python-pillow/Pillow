import pytest
from packaging.version import parse as parse_version

from PIL import Image, ImageDraw, ImageFont, features

from .helper import (
    assert_image_similar_tofile,
    skip_unless_feature,
    skip_unless_feature_version,
)

FONT_SIZE = 20
FONT_PATH = "Tests/fonts/DejaVuSans/DejaVuSans.ttf"

pytestmark = skip_unless_feature("raqm")


def test_english():
    # smoke test, this should not fail
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "TEST", font=ttf, fill=500, direction="ltr")


def test_complex_text():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "اهلا عمان", font=ttf, fill=500)

    target = "Tests/images/test_text.png"
    assert_image_similar_tofile(im, target, 0.5)


def test_y_offset():
    ttf = ImageFont.truetype("Tests/fonts/NotoNastaliqUrdu-Regular.ttf", FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "العالم العربي", font=ttf, fill=500)

    target = "Tests/images/test_y_offset.png"
    assert_image_similar_tofile(im, target, 1.7)


def test_complex_unicode_text():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "السلام عليكم", font=ttf, fill=500)

    target = "Tests/images/test_complex_unicode_text.png"
    assert_image_similar_tofile(im, target, 0.5)

    ttf = ImageFont.truetype("Tests/fonts/KhmerOSBattambang-Regular.ttf", FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "លោកុប្បត្តិ", font=ttf, fill=500)

    target = "Tests/images/test_complex_unicode_text2.png"
    assert_image_similar_tofile(im, target, 2.33)


def test_text_direction_rtl():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "English عربي", font=ttf, fill=500, direction="rtl")

    target = "Tests/images/test_direction_rtl.png"
    assert_image_similar_tofile(im, target, 0.5)


def test_text_direction_ltr():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "سلطنة عمان Oman", font=ttf, fill=500, direction="ltr")

    target = "Tests/images/test_direction_ltr.png"
    assert_image_similar_tofile(im, target, 0.5)


def test_text_direction_rtl2():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "Oman سلطنة عمان", font=ttf, fill=500, direction="rtl")

    target = "Tests/images/test_direction_ltr.png"
    assert_image_similar_tofile(im, target, 0.5)


def test_text_direction_ttb():
    ttf = ImageFont.truetype("Tests/fonts/NotoSansJP-Regular.otf", FONT_SIZE)

    im = Image.new(mode="RGB", size=(100, 300))
    draw = ImageDraw.Draw(im)
    try:
        draw.text((0, 0), "English あい", font=ttf, fill=500, direction="ttb")
    except ValueError as ex:
        if str(ex) == "libraqm 0.7 or greater required for 'ttb' direction":
            pytest.skip("libraqm 0.7 or greater not available")

    target = "Tests/images/test_direction_ttb.png"
    assert_image_similar_tofile(im, target, 2.8)


def test_text_direction_ttb_stroke():
    ttf = ImageFont.truetype("Tests/fonts/NotoSansJP-Regular.otf", 50)

    im = Image.new(mode="RGB", size=(100, 300))
    draw = ImageDraw.Draw(im)
    try:
        draw.text(
            (27, 27),
            "あい",
            font=ttf,
            fill=500,
            direction="ttb",
            stroke_width=2,
            stroke_fill="#0f0",
        )
    except ValueError as ex:
        if str(ex) == "libraqm 0.7 or greater required for 'ttb' direction":
            pytest.skip("libraqm 0.7 or greater not available")

    target = "Tests/images/test_direction_ttb_stroke.png"
    assert_image_similar_tofile(im, target, 19.4)


def test_ligature_features():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "filling", font=ttf, fill=500, features=["-liga"])
    target = "Tests/images/test_ligature_features.png"
    assert_image_similar_tofile(im, target, 0.5)

    liga_size = ttf.getsize("fi", features=["-liga"])
    assert liga_size == (13, 19)


def test_kerning_features():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "TeToAV", font=ttf, fill=500, features=["-kern"])

    target = "Tests/images/test_kerning_features.png"
    assert_image_similar_tofile(im, target, 0.5)


def test_arabictext_features():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text(
        (0, 0),
        "اللغة العربية",
        font=ttf,
        fill=500,
        features=["-fina", "-init", "-medi"],
    )

    target = "Tests/images/test_arabictext_features.png"
    assert_image_similar_tofile(im, target, 0.5)


def test_x_max_and_y_offset():
    ttf = ImageFont.truetype("Tests/fonts/ArefRuqaa-Regular.ttf", 40)

    im = Image.new(mode="RGB", size=(50, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "لح", font=ttf, fill=500)

    target = "Tests/images/test_x_max_and_y_offset.png"
    assert_image_similar_tofile(im, target, 0.5)


def test_language():
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    im = Image.new(mode="RGB", size=(300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), "абвг", font=ttf, fill=500, language="sr")

    target = "Tests/images/test_language.png"
    assert_image_similar_tofile(im, target, 0.5)


@pytest.mark.parametrize("mode", ("L", "1"))
@pytest.mark.parametrize(
    "text, direction, expected",
    (
        ("سلطنة عمان Oman", None, 173.703125),
        ("سلطنة عمان Oman", "ltr", 173.703125),
        ("Oman سلطنة عمان", "rtl", 173.703125),
        ("English عربي", "rtl", 123.796875),
        ("test", "ttb", 80.0),
    ),
    ids=("None", "ltr", "rtl2", "rtl", "ttb"),
)
def test_getlength(mode, text, direction, expected):
    ttf = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    im = Image.new(mode, (1, 1), 0)
    d = ImageDraw.Draw(im)

    try:
        assert d.textlength(text, ttf, direction) == expected
    except ValueError as ex:
        if (
            direction == "ttb"
            and str(ex) == "libraqm 0.7 or greater required for 'ttb' direction"
        ):
            pytest.skip("libraqm 0.7 or greater not available")


@pytest.mark.parametrize("mode", ("L", "1"))
@pytest.mark.parametrize("direction", ("ltr", "ttb"))
@pytest.mark.parametrize(
    "text",
    ("i" + ("\u030C" * 15) + "i", "i" + "\u032C" * 15 + "i", "\u035Cii", "i\u0305i"),
    ids=("caron-above", "caron-below", "double-breve", "overline"),
)
def test_getlength_combine(mode, direction, text):
    if text == "i\u0305i" and direction == "ttb":
        pytest.skip("fails with this font")

    ttf = ImageFont.truetype("Tests/fonts/NotoSans-Regular.ttf", 48)

    try:
        target = ttf.getlength("ii", mode, direction)
        actual = ttf.getlength(text, mode, direction)

        assert actual == target
    except ValueError as ex:
        if (
            direction == "ttb"
            and str(ex) == "libraqm 0.7 or greater required for 'ttb' direction"
        ):
            pytest.skip("libraqm 0.7 or greater not available")


# FreeType 2.5.1 README: Miscellaneous Changes:
# Improved computation of emulated vertical metrics for TrueType fonts.
@skip_unless_feature_version(
    "freetype2", "2.5.1", "FreeType <2.5.1 has incompatible ttb metrics"
)
@pytest.mark.parametrize("anchor", ("lt", "mm", "rb", "sm"))
def test_anchor_ttb(anchor):
    text = "f"
    path = f"Tests/images/test_anchor_ttb_{text}_{anchor}.png"
    f = ImageFont.truetype("Tests/fonts/NotoSans-Regular.ttf", 120)

    im = Image.new("RGB", (200, 400), "white")
    d = ImageDraw.Draw(im)
    d.line(((0, 200), (200, 200)), "gray")
    d.line(((100, 0), (100, 400)), "gray")
    try:
        d.text((100, 200), text, fill="black", anchor=anchor, direction="ttb", font=f)
    except ValueError as ex:
        if str(ex) == "libraqm 0.7 or greater required for 'ttb' direction":
            pytest.skip("libraqm 0.7 or greater not available")

    assert_image_similar_tofile(im, path, 1)  # fails at 5


combine_tests = (
    # extends above (e.g. issue #4553)
    ("caron", "a\u030C\u030C\u030C\u030C\u030Cb", None, None, 0.08),
    ("caron_la", "a\u030C\u030C\u030C\u030C\u030Cb", "la", None, 0.08),
    ("caron_lt", "a\u030C\u030C\u030C\u030C\u030Cb", "lt", None, 0.08),
    ("caron_ls", "a\u030C\u030C\u030C\u030C\u030Cb", "ls", None, 0.08),
    ("caron_ttb", "ca" + ("\u030C" * 15) + "b", None, "ttb", 0.3),
    ("caron_ttb_lt", "ca" + ("\u030C" * 15) + "b", "lt", "ttb", 0.3),
    # extends below
    ("caron_below", "a\u032C\u032C\u032C\u032C\u032Cb", None, None, 0.02),
    ("caron_below_ld", "a\u032C\u032C\u032C\u032C\u032Cb", "ld", None, 0.02),
    ("caron_below_lb", "a\u032C\u032C\u032C\u032C\u032Cb", "lb", None, 0.02),
    ("caron_below_ls", "a\u032C\u032C\u032C\u032C\u032Cb", "ls", None, 0.02),
    ("caron_below_ttb", "a" + ("\u032C" * 15) + "b", None, "ttb", 0.03),
    ("caron_below_ttb_lb", "a" + ("\u032C" * 15) + "b", "lb", "ttb", 0.03),
    # extends to the right (e.g. issue #3745)
    ("double_breve_below", "a\u035Ci", None, None, 0.02),
    ("double_breve_below_ma", "a\u035Ci", "ma", None, 0.02),
    ("double_breve_below_ra", "a\u035Ci", "ra", None, 0.02),
    ("double_breve_below_ttb", "a\u035Cb", None, "ttb", 0.02),
    ("double_breve_below_ttb_rt", "a\u035Cb", "rt", "ttb", 0.02),
    ("double_breve_below_ttb_mt", "a\u035Cb", "mt", "ttb", 0.02),
    ("double_breve_below_ttb_st", "a\u035Cb", "st", "ttb", 0.02),
    # extends to the left (fail=0.064)
    ("overline", "i\u0305", None, None, 0.02),
    ("overline_la", "i\u0305", "la", None, 0.02),
    ("overline_ra", "i\u0305", "ra", None, 0.02),
    ("overline_ttb", "i\u0305", None, "ttb", 0.02),
    ("overline_ttb_rt", "i\u0305", "rt", "ttb", 0.02),
    ("overline_ttb_mt", "i\u0305", "mt", "ttb", 0.02),
    ("overline_ttb_st", "i\u0305", "st", "ttb", 0.02),
)


# this tests various combining characters for anchor alignment and clipping
@pytest.mark.parametrize(
    "name, text, anchor, dir, epsilon", combine_tests, ids=[r[0] for r in combine_tests]
)
def test_combine(name, text, dir, anchor, epsilon):
    if (
        parse_version(features.version_module("freetype2")) < parse_version("2.5.1")
        and dir == "ttb"
    ):
        # FreeType 2.5.1 README: Miscellaneous Changes:
        # Improved computation of emulated vertical metrics for TrueType fonts.
        pytest.skip("FreeType <2.5.1 has incompatible ttb metrics")

    path = f"Tests/images/test_combine_{name}.png"
    f = ImageFont.truetype("Tests/fonts/NotoSans-Regular.ttf", 48)

    im = Image.new("RGB", (400, 400), "white")
    d = ImageDraw.Draw(im)
    d.line(((0, 200), (400, 200)), "gray")
    d.line(((200, 0), (200, 400)), "gray")
    try:
        d.text((200, 200), text, fill="black", anchor=anchor, direction=dir, font=f)
    except ValueError as ex:
        if str(ex) == "libraqm 0.7 or greater required for 'ttb' direction":
            pytest.skip("libraqm 0.7 or greater not available")

    assert_image_similar_tofile(im, path, epsilon)


@pytest.mark.parametrize(
    "anchor, align",
    (
        ("lm", "left"),  # pass with getsize
        ("lm", "center"),  # fail at 2.12
        ("lm", "right"),  # fail at 2.57
        ("mm", "left"),  # fail at 2.12
        ("mm", "center"),  # pass with getsize
        ("mm", "right"),  # fail at 2.12
        ("rm", "left"),  # fail at 2.57
        ("rm", "center"),  # fail at 2.12
        ("rm", "right"),  # pass with getsize
    ),
)
def test_combine_multiline(anchor, align):
    # test that multiline text uses getlength, not getsize or getbbox

    path = f"Tests/images/test_combine_multiline_{anchor}_{align}.png"
    f = ImageFont.truetype("Tests/fonts/NotoSans-Regular.ttf", 48)
    text = "i\u0305\u035C\ntext"  # i with overline and double breve, and a word

    im = Image.new("RGB", (400, 400), "white")
    d = ImageDraw.Draw(im)
    d.line(((0, 200), (400, 200)), "gray")
    d.line(((200, 0), (200, 400)), "gray")
    bbox = d.multiline_textbbox((200, 200), text, anchor=anchor, font=f, align=align)
    d.rectangle(bbox, outline="red")
    d.multiline_text((200, 200), text, fill="black", anchor=anchor, font=f, align=align)

    assert_image_similar_tofile(im, path, 0.015)


def test_anchor_invalid_ttb():
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    im = Image.new("RGB", (100, 100), "white")
    d = ImageDraw.Draw(im)
    d.font = font

    for anchor in ["", "l", "a", "lax", "xa", "la", "ls", "ld", "lx"]:
        pytest.raises(
            ValueError, lambda: font.getmask2("hello", anchor=anchor, direction="ttb")
        )
        pytest.raises(
            ValueError, lambda: font.getbbox("hello", anchor=anchor, direction="ttb")
        )
        pytest.raises(
            ValueError, lambda: d.text((0, 0), "hello", anchor=anchor, direction="ttb")
        )
        pytest.raises(
            ValueError,
            lambda: d.textbbox((0, 0), "hello", anchor=anchor, direction="ttb"),
        )
        pytest.raises(
            ValueError,
            lambda: d.multiline_text(
                (0, 0), "foo\nbar", anchor=anchor, direction="ttb"
            ),
        )
        pytest.raises(
            ValueError,
            lambda: d.multiline_textbbox(
                (0, 0), "foo\nbar", anchor=anchor, direction="ttb"
            ),
        )
    # ttb multiline text does not support anchors at all
    pytest.raises(
        ValueError,
        lambda: d.multiline_text((0, 0), "foo\nbar", anchor="mm", direction="ttb"),
    )
    pytest.raises(
        ValueError,
        lambda: d.multiline_textbbox((0, 0), "foo\nbar", anchor="mm", direction="ttb"),
    )
