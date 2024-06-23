from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont, _util

from .helper import PillowLeakTestCase, features, skip_unless_feature

original_core = ImageFont.core


class TestTTypeFontLeak(PillowLeakTestCase):
    # fails at iteration 3 in main
    iterations = 10
    mem_limit = 4096  # k

    def _test_font(self, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> None:
        im = Image.new("RGB", (255, 255), "white")
        draw = ImageDraw.ImageDraw(im)
        self._test_leak(
            lambda: draw.text(
                (0, 0), "some text " * 1024, font=font, fill="black"  # ~10k
            )
        )

    @skip_unless_feature("freetype2")
    def test_leak(self) -> None:
        ttype = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 20)
        self._test_font(ttype)


class TestDefaultFontLeak(TestTTypeFontLeak):
    # fails at iteration 37 in main
    iterations = 100
    mem_limit = 1024  # k

    def test_leak(self) -> None:
        if features.check_module("freetype2"):
            ImageFont.core = _util.DeferredError(ImportError("Disabled for testing"))
        try:
            default_font = ImageFont.load_default()
        finally:
            ImageFont.core = original_core

        self._test_font(default_font)
