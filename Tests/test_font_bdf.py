from __future__ import annotations

import pytest

from PIL import BdfFontFile, FontFile

filename = "Tests/images/courB08.bdf"


def test_sanity() -> None:
    with open(filename, "rb") as test_file:
        font = BdfFontFile.BdfFontFile(test_file)

    assert isinstance(font, FontFile.FontFile)
    assert len([_f for _f in font.glyph if _f]) == 190


def test_invalid_file() -> None:
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            BdfFontFile.BdfFontFile(fp)
