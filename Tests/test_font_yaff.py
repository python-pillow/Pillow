from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = str(Path(__file__).parent / "fonts" / "test_yaff.yaff")


class TestYaffFont:
    def test_load_yaff(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        assert len(font.glyphs) > 0
        assert font.ascent == 7
        assert font.descent == 2

    def test_load_yaff_pathlib(self) -> None:
        font = ImageFont.yaff(Path(FONT_PATH))
        assert len(font.glyphs) > 0

    def test_load_yaff_fileobj(self) -> None:
        with open(FONT_PATH, "rb") as f:
            font = ImageFont.yaff(f)
        assert len(font.glyphs) > 0

    def test_getmetrics(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        ascent, descent = font.getmetrics()
        assert ascent == 7
        assert descent == 2

    def test_getlength(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        length = font.getlength("A")
        assert length > 0

    def test_getlength_kerning(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        # AV has kerning: right-kerning on A for V is -2, left-kerning on V for A is -1
        length_av = font.getlength("AV")
        length_a = font.getlength("A")
        length_v = font.getlength("V")
        assert length_av < length_a + length_v
        assert length_av == length_a + length_v - 3  # -2 + -1 = -3

    def test_getlength_kerning_at(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        # AT has kerning: right-kerning on A for T is -1
        length_at = font.getlength("AT")
        length_a = font.getlength("A")
        length_t = font.getlength("T")
        assert length_at < length_a + length_t
        assert length_at == length_a + length_t - 1

    def test_getbbox(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        bbox = font.getbbox("A")
        assert bbox[0] == 0
        assert bbox[1] == 0
        assert bbox[2] > 0
        assert bbox[3] == font.ascent + font.descent

    def test_getmask(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        mask = font.getmask("A")
        assert mask is not None
        assert mask.size[0] > 0
        assert mask.size[1] > 0

    def test_getmask_mode_l(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        mask = font.getmask("A", mode="L")
        assert mask is not None

    def test_getmask2(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        mask, offset = font.getmask2("A")
        assert mask is not None
        assert offset == (0, 0)

    def test_render_text(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        im = Image.new("1", (50, 20))
        draw = ImageDraw.Draw(im)
        draw.text((5, 5), "AVA", fill=1, font=font)
        # Check that some pixels were drawn
        assert im.getbbox() is not None

    def test_render_text_rgb(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        im = Image.new("RGB", (50, 20), "white")
        draw = ImageDraw.Draw(im)
        draw.text((5, 5), "A", fill="black", font=font)
        # Check some pixels changed from white
        pixels = list(im.get_flattened_data())
        assert any(p != (255, 255, 255) for p in pixels)

    def test_default_char(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        # Character not in font should use default char (0x3f = '?')
        length_unknown = font.getlength("\u00ff")
        length_question = font.getlength("?")
        assert length_unknown == length_question

    def test_empty_text(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        length = font.getlength("")
        assert length == 0

    def test_bytes_text(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        length = font.getlength(b"A")
        assert length > 0


class TestYaffFontParser:
    def test_parse_unicode_label(self) -> None:
        from PIL.YaffFontFile import _parse_label

        assert _parse_label("u+0041") == [0x41]
        assert _parse_label("U+0041") == [0x41]

    def test_parse_quoted_label(self) -> None:
        from PIL.YaffFontFile import _parse_label

        assert _parse_label("'A'") == [0x41]

    def test_parse_hex_codepoint(self) -> None:
        from PIL.YaffFontFile import _parse_label

        assert _parse_label("0x41") == [0x41]

    def test_parse_decimal_codepoint(self) -> None:
        from PIL.YaffFontFile import _parse_label

        assert _parse_label("65") == [0x41]

    def test_parse_tag_label(self) -> None:
        from PIL.YaffFontFile import _parse_label

        assert _parse_label('"some_tag"') == []

    def test_kerning_values(self) -> None:
        font = ImageFont.yaff(FONT_PATH)
        glyph_a = font.glyphs[0x41]
        assert 0x56 in glyph_a.right_kerning
        assert glyph_a.right_kerning[0x56] == -2
        assert 0x54 in glyph_a.right_kerning
        assert glyph_a.right_kerning[0x54] == -1

        glyph_v = font.glyphs[0x56]
        assert 0x41 in glyph_v.left_kerning
        assert glyph_v.left_kerning[0x41] == -1
