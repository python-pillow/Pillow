# Tests potential DOS of Jpeg2kImagePlugin with 0 length block.
# Run from anywhere that PIL is importable.

from io import BytesIO

from PIL import Image

with Image.open(
    BytesIO(b"\x00\x00\x00\x0cjP\x20\x20\x0d\x0a\x87\x0a\x00\x00\x00\x00hang")
):
    pass
