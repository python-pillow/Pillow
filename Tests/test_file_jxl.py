from __future__ import annotations

import io

import pytest

from PIL import Image

imagecodecs = pytest.importorskip("imagecodecs", reason="JPEG XL requires imagecodecs")


def test_jxl_roundtrip() -> None:
    im = Image.new("RGB", (24, 24), (30, 120, 200))
    im.info["lossless"] = True
    buf = io.BytesIO()
    im.save(buf, format="JXL")
    buf.seek(0)
    assert buf.read(2) == b"\xff\x0a"  # JPEG XL codestream signature

    buf.seek(0)
    with Image.open(buf) as reloaded:
        assert reloaded.format == "JXL"
        assert reloaded.size == (24, 24)
        assert reloaded.mode == "RGB"
        assert list(reloaded.getdata()) == list(im.getdata())
