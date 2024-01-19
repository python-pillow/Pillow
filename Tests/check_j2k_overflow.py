from __future__ import annotations
from pathlib import PosixPath
import pytest

from PIL import Image


def test_j2k_overflow(tmp_path: PosixPath) -> None:
    im = Image.new("RGBA", (1024, 131584))
    target = str(tmp_path / "temp.jpc")
    with pytest.raises(OSError):
        im.save(target)
