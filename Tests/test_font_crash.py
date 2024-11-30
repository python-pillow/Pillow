from __future__ import annotations

import pytest

from PIL import Image, ImageDraw, ImageFont

from .helper import skip_unless_feature


class TestFontCrash:
    def _fuzz_font(self, font: ImageFont.FreeTypeFont) -> None:
        # from fuzzers.fuzz_font
        font.getbbox("ABC")
        font.getmask("test text")
        with Image.new(mode="RGBA", size=(200, 200)) as im:
            draw = ImageDraw.Draw(im)
            draw.multiline_textbbox((10, 10), "ABC\nAaaa", font, stroke_width=2)
            draw.text((10, 10), "Test Text", font=font, fill="#000")

    @skip_unless_feature("freetype2")
    def test_segfault(self) -> None:
        with pytest.raises(OSError):
            font = ImageFont.truetype("Tests/fonts/fuzz_font-5203009437302784")
            self._fuzz_font(font)
