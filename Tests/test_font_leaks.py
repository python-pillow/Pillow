from __future__ import annotations

import pytest

from PIL import Image, ImageDraw, ImageFont, _util

from .helper import PillowLeakTestCase, features, skip_unless_feature

original_core = ImageFont.core


class TestFontLeak(PillowLeakTestCase):
    def _test_font(self, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> None:
        im = Image.new("RGB", (255, 255), "white")
        draw = ImageDraw.ImageDraw(im)
        self._test_leak(
            lambda: draw.text(
                (0, 0), "some text " * 1024, font=font, fill="black"  # ~10k
            )
        )


class TestTTypeFontLeak(TestFontLeak):
    # fails at iteration 3 in main
    iterations = 10
    mem_limit = 4096  # k

    @skip_unless_feature("freetype2")
    def test_leak(self) -> None:
        ttype = ImageFont.truetype("Tests/fonts/FreeMono.ttf", 20)
        self._test_font(ttype)


class TestDefaultFontLeak(TestFontLeak):
    # fails at iteration 37 in main
    iterations = 100
    mem_limit = 1024  # k

    def test_leak(self, monkeypatch: pytest.MonkeyPatch) -> None:
        if features.check_module("freetype2"):
            monkeypatch.setattr(
                ImageFont,
                "core",
                _util.DeferredError(ImportError("Disabled for testing")),
            )
        default_font = ImageFont.load_default()
        self._test_font(default_font)
