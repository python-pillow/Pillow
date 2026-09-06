# Tests potential DOS of IcnsImagePlugin with 0 length block.
# Run from anywhere that PIL is importable.
from __future__ import annotations

from io import BytesIO

from PIL import Image

with Image.open(BytesIO(b"icns\x00\x00\x00\x10hang\x00\x00\x00\x00")):
    pass
