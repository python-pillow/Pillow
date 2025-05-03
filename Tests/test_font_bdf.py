from __future__ import annotations

import io

import pytest

from PIL import BdfFontFile, FontFile

filename = "Tests/images/courB08.bdf"


def test_sanity() -> None:
    with open(filename, "rb") as fp:
        font = BdfFontFile.BdfFontFile(fp)

    assert isinstance(font, FontFile.FontFile)
    assert len([_f for _f in font.glyph if _f]) == 190


def test_zero_width_chars() -> None:
    with open(filename, "rb") as fp:
        data = fp.read()
    data = data[:2650] + b"\x00\x00" + data[2652:]
    BdfFontFile.BdfFontFile(io.BytesIO(data))


def test_invalid_file() -> None:
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            BdfFontFile.BdfFontFile(fp)
