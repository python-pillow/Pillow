# Tests potential DOS of IcnsImagePlugin with 0 length block.
# Run from anywhere that PIL is importable.

from PIL import Image
from io import BytesIO

if bytes is str:
    Image.open(BytesIO(bytes('icns\x00\x00\x00\x10hang\x00\x00\x00\x00')))
else:
    Image.open(BytesIO(bytes('icns\x00\x00\x00\x10hang\x00\x00\x00\x00',
                             'latin-1')))
