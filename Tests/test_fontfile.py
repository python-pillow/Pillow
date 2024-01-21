from __future__ import annotations

import pytest

from PIL import FontFile


def test_save(tmp_path):
    tempname = str(tmp_path / "temp.pil")

    font = FontFile.FontFile()
    with pytest.raises(ValueError):
        font.save(tempname)
