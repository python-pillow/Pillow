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


class TestImageFont:
    LAYOUT_ENGINE = ImageFont.LAYOUT_BASIC

    def get_font(self):
        return ImageFont.truetype(
            FONT_PATH, FONT_SIZE, layout_engine=self.LAYOUT_ENGINE
        )

    def test_sanity(self):
        assert re.search(r"\d+\.\d+\.\d+$", features.version_module("freetype2"))

    def test_font_properties(self):
        ttf = self.get_font()
        assert ttf.path == FONT_PATH
        assert ttf.size == FONT_SIZE

        ttf_copy = ttf.font_variant()
        assert ttf_copy.path == FONT_PATH
        assert ttf_copy.size == FONT_SIZE

        ttf_copy = ttf.font_variant(size=FONT_SIZE + 1)
        assert ttf_copy.size == FONT_SIZE + 1

        second_font_path = "Tests/fonts/DejaVuSans/DejaVuSans.ttf"
        ttf_copy = ttf.font_variant(font=second_font_path)
        assert ttf_copy.path == second_font_path

    def test_font_with_name(self):
        self.get_font()
        self._render(FONT_PATH)

    def _font_as_bytes(self):
        with open(FONT_PATH, "rb") as f:
            font_bytes = BytesIO(f.read())
        return font_bytes

    def test_font_with_filelike(self):
        ImageFont.truetype(
            self._font_as_bytes(), FONT_SIZE, layout_engine=self.LAYOUT_ENGINE
        )
        self._render(self._font_as_bytes())
        # Usage note:  making two fonts from the same buffer fails.
        # shared_bytes = self._font_as_bytes()
        # self._render(shared_bytes)
        # with pytest.raises(Exception):
        #   _render(shared_bytes)

    def test_font_with_open_file(self):
        with open(FONT_PATH, "rb") as f:
            self._render(f)

    def test_non_ascii_path(self, tmp_path):
        tempfile = str(tmp_path / ("temp_" + chr(128) + ".ttf"))
        try:
            shutil.copy(FONT_PATH, tempfile)
        except UnicodeEncodeError:
            pytest.skip("Non-ASCII path could not be created")

        ImageFont.truetype(tempfile, FONT_SIZE)

    def test_unavailable_layout_engine(self):
        have_raqm = ImageFont.core.HAVE_RAQM
        ImageFont.core.HAVE_RAQM = False

        try:
            ttf = ImageFont.truetype(
                FONT_PATH, FONT_SIZE, layout_engine=ImageFont.LAYOUT_RAQM
            )
        finally:
            ImageFont.core.HAVE_RAQM = have_raqm

        assert ttf.layout_engine == ImageFont.LAYOUT_BASIC

    def _render(self, font):
        txt = "Hello World!"
        ttf = ImageFont.truetype(font, FONT_SIZE, layout_engine=self.LAYOUT_ENGINE)
        ttf.getsize(txt)

        img = Image.new("RGB", (256, 64), "white")
        d = ImageDraw.Draw(img)
        d.text((10, 10), txt, font=ttf, fill="black")

        return img

    def test_render_equal(self):
        img_path = self._render(FONT_PATH)
        with open(FONT_PATH, "rb") as f:
            font_filelike = BytesIO(f.read())
        img_filelike = self._render(font_filelike)

        assert_image_equal(img_path, img_filelike)

    def test_transparent_background(self):
        im = Image.new(mode="RGBA", size=(300, 100))
        draw = ImageDraw.Draw(im)
        ttf = self.get_font()

        txt = "Hello World!"
        draw.text((10, 10), txt, font=ttf)

        target = "Tests/images/transparent_background_text.png"
        assert_image_similar_tofile(im, target, 4.09)

        target = "Tests/images/transparent_background_text_L.png"
        assert_image_similar_tofile(im.convert("L"), target, 0.01)

    def test_I16(self):
        im = Image.new(mode="I;16", size=(300, 100))
        draw = ImageDraw.Draw(im)
        ttf = self.get_font()

        txt = "Hello World!"
        draw.text((10, 10), txt, font=ttf)

        target = "Tests/images/transparent_background_text_L.png"
        assert_image_similar_tofile(im.convert("L"), target, 0.01)

    def test_textsize_equal(self):
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        ttf = self.get_font()

        txt = "Hello World!"
        size = draw.textsize(txt, ttf)
        draw.text((10, 10), txt, font=ttf)
        draw.rectangle((10, 10, 10 + size[0], 10 + size[1]))

        # Epsilon ~.5 fails with FreeType 2.7
        assert_image_similar_tofile(
            im, "Tests/images/rectangle_surrounding_text.png", 2.5
        )

    @pytest.mark.parametrize(
        "text, mode, font, size, length_basic, length_raqm",
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
    def test_getlength(self, text, mode, font, size, length_basic, length_raqm):
        f = ImageFont.truetype(
            "Tests/fonts/" + font, size, layout_engine=self.LAYOUT_ENGINE
        )

        im = Image.new(mode, (1, 1), 0)
        d = ImageDraw.Draw(im)

        if self.LAYOUT_ENGINE == ImageFont.LAYOUT_BASIC:
            length = d.textlength(text, f)
            assert length == length_basic
        else:
            # disable kerning, kerning metrics changed
            length = d.textlength(text, f, features=["-kern"])
            assert length == length_raqm

    def test_render_multiline(self):
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        ttf = self.get_font()
        line_spacing = draw.textsize("A", font=ttf)[1] + 4
        lines = TEST_TEXT.split("\n")
        y = 0
        for line in lines:
            draw.text((0, y), line, font=ttf)
            y += line_spacing

        # some versions of freetype have different horizontal spacing.
        # setting a tight epsilon, I'm showing the original test failure
        # at epsilon = ~38.
        assert_image_similar_tofile(im, "Tests/images/multiline_text.png", 6.2)

    def test_render_multiline_text(self):
        ttf = self.get_font()

        # Test that text() correctly connects to multiline_text()
        # and that align defaults to left
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), TEST_TEXT, font=ttf)

        # Epsilon ~.5 fails with FreeType 2.7
        assert_image_similar_tofile(im, "Tests/images/multiline_text.png", 6.2)

        # Test that text() can pass on additional arguments
        # to multiline_text()
        draw.text(
            (0, 0), TEST_TEXT, fill=None, font=ttf, anchor=None, spacing=4, align="left"
        )
        draw.text((0, 0), TEST_TEXT, None, ttf, None, 4, "left")

        # Test align center and right
        for align, ext in {"center": "_center", "right": "_right"}.items():
            im = Image.new(mode="RGB", size=(300, 100))
            draw = ImageDraw.Draw(im)
            draw.multiline_text((0, 0), TEST_TEXT, font=ttf, align=align)

            # Epsilon ~.5 fails with FreeType 2.7
            assert_image_similar_tofile(
                im, "Tests/images/multiline_text" + ext + ".png", 6.2
            )

    def test_unknown_align(self):
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        ttf = self.get_font()

        # Act/Assert
        with pytest.raises(ValueError):
            draw.multiline_text((0, 0), TEST_TEXT, font=ttf, align="unknown")

    def test_draw_align(self):
        im = Image.new("RGB", (300, 100), "white")
        draw = ImageDraw.Draw(im)
        ttf = self.get_font()
        line = "some text"
        draw.text((100, 40), line, (0, 0, 0), font=ttf, align="left")

    def test_multiline_size(self):
        ttf = self.get_font()
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)

        # Test that textsize() correctly connects to multiline_textsize()
        assert draw.textsize(TEST_TEXT, font=ttf) == draw.multiline_textsize(
            TEST_TEXT, font=ttf
        )

        # Test that multiline_textsize corresponds to ImageFont.textsize()
        # for single line text
        assert ttf.getsize("A") == draw.multiline_textsize("A", font=ttf)

        # Test that textsize() can pass on additional arguments
        # to multiline_textsize()
        draw.textsize(TEST_TEXT, font=ttf, spacing=4)
        draw.textsize(TEST_TEXT, ttf, 4)

    def test_multiline_width(self):
        ttf = self.get_font()
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)

        assert (
            draw.textsize("longest line", font=ttf)[0]
            == draw.multiline_textsize("longest line\nline", font=ttf)[0]
        )

    def test_multiline_spacing(self):
        ttf = self.get_font()

        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)
        draw.multiline_text((0, 0), TEST_TEXT, font=ttf, spacing=10)

        # Epsilon ~.5 fails with FreeType 2.7
        assert_image_similar_tofile(im, "Tests/images/multiline_text_spacing.png", 6.2)

    def test_rotated_transposed_font(self):
        img_grey = Image.new("L", (100, 100))
        draw = ImageDraw.Draw(img_grey)
        word = "testing"
        font = self.get_font()

        orientation = Image.ROTATE_90
        transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

        # Original font
        draw.font = font
        box_size_a = draw.textsize(word)

        # Rotated font
        draw.font = transposed_font
        box_size_b = draw.textsize(word)

        # Check (w,h) of box a is (h,w) of box b
        assert box_size_a[0] == box_size_b[1]
        assert box_size_a[1] == box_size_b[0]

    def test_unrotated_transposed_font(self):
        img_grey = Image.new("L", (100, 100))
        draw = ImageDraw.Draw(img_grey)
        word = "testing"
        font = self.get_font()

        orientation = None
        transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

        # Original font
        draw.font = font
        box_size_a = draw.textsize(word)

        # Rotated font
        draw.font = transposed_font
        box_size_b = draw.textsize(word)

        # Check boxes a and b are same size
        assert box_size_a == box_size_b

    def test_rotated_transposed_font_get_mask(self):
        # Arrange
        text = "mask this"
        font = self.get_font()
        orientation = Image.ROTATE_90
        transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

        # Act
        mask = transposed_font.getmask(text)

        # Assert
        assert mask.size == (13, 108)

    def test_unrotated_transposed_font_get_mask(self):
        # Arrange
        text = "mask this"
        font = self.get_font()
        orientation = None
        transposed_font = ImageFont.TransposedFont(font, orientation=orientation)

        # Act
        mask = transposed_font.getmask(text)

        # Assert
        assert mask.size == (108, 13)

    def test_free_type_font_get_name(self):
        # Arrange
        font = self.get_font()

        # Act
        name = font.getname()

        # Assert
        assert ("FreeMono", "Regular") == name

    def test_free_type_font_get_metrics(self):
        # Arrange
        font = self.get_font()

        # Act
        ascent, descent = font.getmetrics()

        # Assert
        assert isinstance(ascent, int)
        assert isinstance(descent, int)
        assert (ascent, descent) == (16, 4)  # too exact check?

    def test_free_type_font_get_offset(self):
        # Arrange
        font = self.get_font()
        text = "offset this"

        # Act
        offset = font.getoffset(text)

        # Assert
        assert offset == (0, 3)

    def test_free_type_font_get_mask(self):
        # Arrange
        font = self.get_font()
        text = "mask this"

        # Act
        mask = font.getmask(text)

        # Assert
        assert mask.size == (108, 13)

    def test_load_path_not_found(self):
        # Arrange
        filename = "somefilenamethatdoesntexist.ttf"

        # Act/Assert
        with pytest.raises(OSError):
            ImageFont.load_path(filename)
        with pytest.raises(OSError):
            ImageFont.truetype(filename)

    def test_load_non_font_bytes(self):
        with open("Tests/images/hopper.jpg", "rb") as f:
            with pytest.raises(OSError):
                ImageFont.truetype(f)

    def test_default_font(self):
        # Arrange
        txt = 'This is a "better than nothing" default font.'
        im = Image.new(mode="RGB", size=(300, 100))
        draw = ImageDraw.Draw(im)

        # Act
        default_font = ImageFont.load_default()
        draw.text((10, 10), txt, font=default_font)

        # Assert
        assert_image_equal_tofile(im, "Tests/images/default_font.png")

    def test_getsize_empty(self):
        # issue #2614
        font = self.get_font()
        # should not crash.
        assert (0, 0) == font.getsize("")

    def test_render_empty(self):
        # issue 2666
        font = self.get_font()
        im = Image.new(mode="RGB", size=(300, 100))
        target = im.copy()
        draw = ImageDraw.Draw(im)
        # should not crash here.
        draw.text((10, 10), "", font=font)
        assert_image_equal(im, target)

    def test_unicode_pilfont(self):
        # should not segfault, should return UnicodeDecodeError
        # issue #2826
        font = ImageFont.load_default()
        with pytest.raises(UnicodeEncodeError):
            font.getsize("’")

    def test_unicode_extended(self):
        # issue #3777
        text = "A\u278A\U0001F12B"
        target = "Tests/images/unicode_extended.png"

        ttf = ImageFont.truetype(
            "Tests/fonts/NotoSansSymbols-Regular.ttf",
            FONT_SIZE,
            layout_engine=self.LAYOUT_ENGINE,
        )
        img = Image.new("RGB", (100, 60))
        d = ImageDraw.Draw(img)
        d.text((10, 10), text, font=ttf)

        # fails with 14.7
        assert_image_similar_tofile(img, target, 6.2)

    def _test_fake_loading_font(self, monkeypatch, path_to_fake, fontname):
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

    @pytest.mark.skipif(is_win32(), reason="requires Unix or macOS")
    def test_find_linux_font(self, monkeypatch):
        # A lot of mocking here - this is more for hitting code and
        # catching syntax like errors
        font_directory = "/usr/local/share/fonts"
        monkeypatch.setattr(sys, "platform", "linux")
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
        # Test that the font loads both with and without the
        # extension
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Arial.ttf", "Arial.ttf"
        )
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Arial.ttf", "Arial"
        )

        # Test that non-ttf fonts can be found without the
        # extension
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Single.otf", "Single"
        )

        # Test that ttf fonts are preferred if the extension is
        # not specified
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Duplicate.ttf", "Duplicate"
        )

    @pytest.mark.skipif(is_win32(), reason="requires Unix or macOS")
    def test_find_macos_font(self, monkeypatch):
        # Like the linux test, more cover hitting code rather than testing
        # correctness.
        font_directory = "/System/Library/Fonts"
        monkeypatch.setattr(sys, "platform", "darwin")

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
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Arial.ttf", "Arial.ttf"
        )
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Arial.ttf", "Arial"
        )
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Single.otf", "Single"
        )
        self._test_fake_loading_font(
            monkeypatch, font_directory + "/Duplicate.ttf", "Duplicate"
        )

    def test_imagefont_getters(self):
        # Arrange
        t = self.get_font()

        # Act / Assert
        assert t.getmetrics() == (16, 4)
        assert t.font.ascent == 16
        assert t.font.descent == 4
        assert t.font.height == 20
        assert t.font.x_ppem == 20
        assert t.font.y_ppem == 20
        assert t.font.glyphs == 4177
        assert t.getsize("A") == (12, 16)
        assert t.getsize("AB") == (24, 16)
        assert t.getsize("M") == (12, 16)
        assert t.getsize("y") == (12, 20)
        assert t.getsize("a") == (12, 16)
        assert t.getsize_multiline("A") == (12, 16)
        assert t.getsize_multiline("AB") == (24, 16)
        assert t.getsize_multiline("a") == (12, 16)
        assert t.getsize_multiline("ABC\n") == (36, 36)
        assert t.getsize_multiline("ABC\nA") == (36, 36)
        assert t.getsize_multiline("ABC\nAaaa") == (48, 36)

    def test_getsize_stroke(self):
        # Arrange
        t = self.get_font()

        # Act / Assert
        for stroke_width in [0, 2]:
            assert t.getsize("A", stroke_width=stroke_width) == (
                12 + stroke_width * 2,
                16 + stroke_width * 2,
            )
            assert t.getsize_multiline("ABC\nAaaa", stroke_width=stroke_width) == (
                48 + stroke_width * 2,
                36 + stroke_width * 4,
            )

    def test_complex_font_settings(self):
        # Arrange
        t = self.get_font()
        # Act / Assert
        if t.layout_engine == ImageFont.LAYOUT_BASIC:
            with pytest.raises(KeyError):
                t.getmask("абвг", direction="rtl")
            with pytest.raises(KeyError):
                t.getmask("абвг", features=["-kern"])
            with pytest.raises(KeyError):
                t.getmask("абвг", language="sr")

    def test_variation_get(self):
        font = self.get_font()

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

    def _check_text(self, font, path, epsilon):
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

    def test_variation_set_by_name(self):
        font = self.get_font()

        freetype = parse_version(features.version_module("freetype2"))
        if freetype < parse_version("2.9.1"):
            with pytest.raises(NotImplementedError):
                font.set_variation_by_name("Bold")
            return

        with pytest.raises(OSError):
            font.set_variation_by_name("Bold")

        font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf", 36)
        self._check_text(font, "Tests/images/variation_adobe.png", 11)
        for name in ["Bold", b"Bold"]:
            font.set_variation_by_name(name)
        self._check_text(font, "Tests/images/variation_adobe_name.png", 11)

        font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf", 36)
        self._check_text(font, "Tests/images/variation_tiny.png", 40)
        for name in ["200", b"200"]:
            font.set_variation_by_name(name)
        self._check_text(font, "Tests/images/variation_tiny_name.png", 40)

    def test_variation_set_by_axes(self):
        font = self.get_font()

        freetype = parse_version(features.version_module("freetype2"))
        if freetype < parse_version("2.9.1"):
            with pytest.raises(NotImplementedError):
                font.set_variation_by_axes([100])
            return

        with pytest.raises(OSError):
            font.set_variation_by_axes([500, 50])

        font = ImageFont.truetype("Tests/fonts/AdobeVFPrototype.ttf", 36)
        font.set_variation_by_axes([500, 50])
        self._check_text(font, "Tests/images/variation_adobe_axes.png", 11.05)

        font = ImageFont.truetype("Tests/fonts/TINY5x3GX.ttf", 36)
        font.set_variation_by_axes([100])
        self._check_text(font, "Tests/images/variation_tiny_axes.png", 32.5)

    def test_textbbox_non_freetypefont(self):
        im = Image.new("RGB", (200, 200))
        d = ImageDraw.Draw(im)
        default_font = ImageFont.load_default()
        with pytest.raises(ValueError):
            d.textbbox((0, 0), "test", font=default_font)

    @pytest.mark.parametrize(
        "anchor, left, left_old, top",
        (
            # test horizontal anchors
            ("ls", 0, 0, -36),
            ("ms", -64, -65, -36),
            ("rs", -128, -129, -36),
            # test vertical anchors
            ("ma", -64, -65, 16),
            ("mt", -64, -65, 0),
            ("mm", -64, -65, -17),
            ("mb", -64, -65, -44),
            ("md", -64, -65, -51),
        ),
        ids=("ls", "ms", "rs", "ma", "mt", "mm", "mb", "md"),
    )
    def test_anchor(self, anchor, left, left_old, top):
        name, text = "quick", "Quick"
        path = f"Tests/images/test_anchor_{name}_{anchor}.png"

        freetype = parse_version(features.version_module("freetype2"))
        if freetype < parse_version("2.4"):
            width, height = (129, 44)
            left = left_old
        elif self.LAYOUT_ENGINE == ImageFont.LAYOUT_RAQM:
            width, height = (129, 44)
        else:
            width, height = (128, 44)

        bbox_expected = (left, top, left + width, top + height)

        f = ImageFont.truetype(
            "Tests/fonts/NotoSans-Regular.ttf", 48, layout_engine=self.LAYOUT_ENGINE
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
    def test_anchor_multiline(self, anchor, align):
        target = f"Tests/images/test_anchor_multiline_{anchor}_{align}.png"
        text = "a\nlong\ntext sample"

        f = ImageFont.truetype(
            "Tests/fonts/NotoSans-Regular.ttf", 48, layout_engine=self.LAYOUT_ENGINE
        )

        # test render
        im = Image.new("RGB", (600, 400), "white")
        d = ImageDraw.Draw(im)
        d.line(((0, 200), (600, 200)), "gray")
        d.line(((300, 0), (300, 400)), "gray")
        d.multiline_text(
            (300, 200), text, fill="black", anchor=anchor, font=f, align=align
        )

        assert_image_similar_tofile(im, target, 4)

    def test_anchor_invalid(self):
        font = self.get_font()
        im = Image.new("RGB", (100, 100), "white")
        d = ImageDraw.Draw(im)
        d.font = font

        for anchor in ["", "l", "a", "lax", "sa", "xa", "lx"]:
            pytest.raises(ValueError, lambda: font.getmask2("hello", anchor=anchor))
            pytest.raises(ValueError, lambda: font.getbbox("hello", anchor=anchor))
            pytest.raises(ValueError, lambda: d.text((0, 0), "hello", anchor=anchor))
            pytest.raises(
                ValueError, lambda: d.textbbox((0, 0), "hello", anchor=anchor)
            )
            pytest.raises(
                ValueError, lambda: d.multiline_text((0, 0), "foo\nbar", anchor=anchor)
            )
            pytest.raises(
                ValueError,
                lambda: d.multiline_textbbox((0, 0), "foo\nbar", anchor=anchor),
            )
        for anchor in ["lt", "lb"]:
            pytest.raises(
                ValueError, lambda: d.multiline_text((0, 0), "foo\nbar", anchor=anchor)
            )
            pytest.raises(
                ValueError,
                lambda: d.multiline_textbbox((0, 0), "foo\nbar", anchor=anchor),
            )

    @skip_unless_feature("freetype2")
    @pytest.mark.parametrize("bpp", (1, 2, 4, 8))
    def test_bitmap_font(self, bpp):
        text = "Bitmap Font"
        layout_name = ["basic", "raqm"][self.LAYOUT_ENGINE]
        target = f"Tests/images/bitmap_font_{bpp}_{layout_name}.png"
        font = ImageFont.truetype(
            f"Tests/fonts/DejaVuSans/DejaVuSans-24-{bpp}-stripped.ttf",
            24,
            layout_engine=self.LAYOUT_ENGINE,
        )

        im = Image.new("RGB", (160, 35), "white")
        draw = ImageDraw.Draw(im)
        draw.text((2, 2), text, "black", font)

        assert_image_equal_tofile(im, target)

    def test_bitmap_font_stroke(self):
        text = "Bitmap Font"
        layout_name = ["basic", "raqm"][self.LAYOUT_ENGINE]
        target = f"Tests/images/bitmap_font_stroke_{layout_name}.png"
        font = ImageFont.truetype(
            "Tests/fonts/DejaVuSans/DejaVuSans-24-8-stripped.ttf",
            24,
            layout_engine=self.LAYOUT_ENGINE,
        )

        im = Image.new("RGB", (160, 35), "white")
        draw = ImageDraw.Draw(im)
        draw.text((2, 2), text, "black", font, stroke_width=2, stroke_fill="red")

        assert_image_similar_tofile(im, target, 0.03)

    def test_standard_embedded_color(self):
        txt = "Hello World!"
        ttf = ImageFont.truetype(FONT_PATH, 40, layout_engine=self.LAYOUT_ENGINE)
        ttf.getsize(txt)

        im = Image.new("RGB", (300, 64), "white")
        d = ImageDraw.Draw(im)
        d.text((10, 10), txt, font=ttf, fill="#fa6", embedded_color=True)

        assert_image_similar_tofile(im, "Tests/images/standard_embedded.png", 6.2)

    @skip_unless_feature_version("freetype2", "2.5.0")
    def test_cbdt(self):
        try:
            font = ImageFont.truetype(
                "Tests/fonts/NotoColorEmoji.ttf",
                size=109,
                layout_engine=self.LAYOUT_ENGINE,
            )

            im = Image.new("RGB", (150, 150), "white")
            d = ImageDraw.Draw(im)

            d.text((10, 10), "\U0001f469", font=font, embedded_color=True)

            assert_image_similar_tofile(im, "Tests/images/cbdt_notocoloremoji.png", 6.2)
        except IOError as e:  # pragma: no cover
            assert str(e) in ("unimplemented feature", "unknown file format")
            pytest.skip("freetype compiled without libpng or CBDT support")

    @skip_unless_feature_version("freetype2", "2.5.0")
    def test_cbdt_mask(self):
        try:
            font = ImageFont.truetype(
                "Tests/fonts/NotoColorEmoji.ttf",
                size=109,
                layout_engine=self.LAYOUT_ENGINE,
            )

            im = Image.new("RGB", (150, 150), "white")
            d = ImageDraw.Draw(im)

            d.text((10, 10), "\U0001f469", "black", font=font)

            assert_image_similar_tofile(
                im, "Tests/images/cbdt_notocoloremoji_mask.png", 6.2
            )
        except IOError as e:  # pragma: no cover
            assert str(e) in ("unimplemented feature", "unknown file format")
            pytest.skip("freetype compiled without libpng or CBDT support")

    @skip_unless_feature_version("freetype2", "2.5.1")
    def test_sbix(self):
        try:
            font = ImageFont.truetype(
                "Tests/fonts/chromacheck-sbix.woff",
                size=300,
                layout_engine=self.LAYOUT_ENGINE,
            )

            im = Image.new("RGB", (400, 400), "white")
            d = ImageDraw.Draw(im)

            d.text((50, 50), "\uE901", font=font, embedded_color=True)

            assert_image_similar_tofile(im, "Tests/images/chromacheck-sbix.png", 1)
        except IOError as e:  # pragma: no cover
            assert str(e) in ("unimplemented feature", "unknown file format")
            pytest.skip("freetype compiled without libpng or SBIX support")

    @skip_unless_feature_version("freetype2", "2.5.1")
    def test_sbix_mask(self):
        try:
            font = ImageFont.truetype(
                "Tests/fonts/chromacheck-sbix.woff",
                size=300,
                layout_engine=self.LAYOUT_ENGINE,
            )

            im = Image.new("RGB", (400, 400), "white")
            d = ImageDraw.Draw(im)

            d.text((50, 50), "\uE901", (100, 0, 0), font=font)

            assert_image_similar_tofile(im, "Tests/images/chromacheck-sbix_mask.png", 1)
        except IOError as e:  # pragma: no cover
            assert str(e) in ("unimplemented feature", "unknown file format")
            pytest.skip("freetype compiled without libpng or SBIX support")

    @skip_unless_feature_version("freetype2", "2.10.0")
    def test_colr(self):
        font = ImageFont.truetype(
            "Tests/fonts/BungeeColor-Regular_colr_Windows.ttf",
            size=64,
            layout_engine=self.LAYOUT_ENGINE,
        )

        im = Image.new("RGB", (300, 75), "white")
        d = ImageDraw.Draw(im)

        d.text((15, 5), "Bungee", font=font, embedded_color=True)

        assert_image_similar_tofile(im, "Tests/images/colr_bungee.png", 21)

    @skip_unless_feature_version("freetype2", "2.10.0")
    def test_colr_mask(self):
        font = ImageFont.truetype(
            "Tests/fonts/BungeeColor-Regular_colr_Windows.ttf",
            size=64,
            layout_engine=self.LAYOUT_ENGINE,
        )

        im = Image.new("RGB", (300, 75), "white")
        d = ImageDraw.Draw(im)

        d.text((15, 5), "Bungee", "black", font=font)

        assert_image_similar_tofile(im, "Tests/images/colr_bungee_mask.png", 22)


@skip_unless_feature("raqm")
class TestImageFont_RaqmLayout(TestImageFont):
    LAYOUT_ENGINE = ImageFont.LAYOUT_RAQM


@skip_unless_feature_version("freetype2", "2.4", "Different metrics")
def test_render_mono_size():
    # issue 4177

    im = Image.new("P", (100, 30), "white")
    draw = ImageDraw.Draw(im)
    ttf = ImageFont.truetype(
        "Tests/fonts/DejaVuSans/DejaVuSans.ttf",
        18,
        layout_engine=ImageFont.LAYOUT_BASIC,
    )

    draw.text((10, 10), "r" * 10, "black", ttf)
    assert_image_equal_tofile(im, "Tests/images/text_mono.gif")


def test_freetype_deprecation(monkeypatch):
    # Arrange: mock features.version_module to return fake FreeType version
    def fake_version_module(module):
        return "2.7"

    monkeypatch.setattr(features, "version_module", fake_version_module)

    # Act / Assert
    with pytest.warns(DeprecationWarning):
        ImageFont.truetype(FONT_PATH, FONT_SIZE)


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/fonts/oom-e8e927ba6c0d38274a37c1567560eb33baf74627.ttf",
    ],
)
def test_oom(test_file):
    with open(test_file, "rb") as f:
        font = ImageFont.truetype(BytesIO(f.read()))
        with pytest.raises(Image.DecompressionBombError):
            font.getmask("Test Text")
