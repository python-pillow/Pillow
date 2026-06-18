from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from PIL import FontFile, Image


def test_puti16() -> None:
    fp = BytesIO()
    FontFile.puti16(fp, (0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
    assert fp.getvalue() == (
        b"\x00\x00\x00\x01\x00\x02\x00\x03\x00\x04"
        b"\x00\x05\x00\x06\x00\x07\x00\x08\x00\t"
    )


def test_compile() -> None:
    font = FontFile.FontFile()
    font.glyph[0] = ((0, 0), (0, 0, 0, 0), (0, 0, 0, 1), Image.new("L", (0, 0)))
    font.compile()
    assert font.ysize == 1

    font.ysize = 2
    font.compile()

    # Assert that compiling again did not change anything
    assert font.ysize == 2


def test_save(tmp_path: Path) -> None:
    tempname = str(tmp_path / "temp.pil")

    font = FontFile.FontFile()
    with pytest.raises(ValueError, match="No bitmap created"):
        font.save(tempname)


def test_to_imagefont() -> None:
    font = FontFile.FontFile()
    with pytest.raises(ValueError, match="No bitmap created"):
        font.to_imagefont()
