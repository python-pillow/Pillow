from __future__ import annotations

import pytest

from PIL import ImageFont, ImageText

from .helper import skip_unless_feature

FONT_PATH = "Tests/fonts/FreeMono.ttf"


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
    return ImageFont.truetype(FONT_PATH, 20, layout_engine=layout_engine)


def test_get_length(font: ImageFont.FreeTypeFont) -> None:
    assert ImageText.ImageText("A", font).get_length() == 12
    assert ImageText.ImageText("AB", font).get_length() == 24
    assert ImageText.ImageText("M", font).get_length() == 12
    assert ImageText.ImageText("y", font).get_length() == 12
    assert ImageText.ImageText("a", font).get_length() == 12


def test_get_bbox(font: ImageFont.FreeTypeFont) -> None:
    assert ImageText.ImageText("A", font).get_bbox() == (0, 4, 12, 16)
    assert ImageText.ImageText("AB", font).get_bbox() == (0, 4, 24, 16)
    assert ImageText.ImageText("M", font).get_bbox() == (0, 4, 12, 16)
    assert ImageText.ImageText("y", font).get_bbox() == (0, 7, 12, 20)
    assert ImageText.ImageText("a", font).get_bbox() == (0, 7, 12, 16)
