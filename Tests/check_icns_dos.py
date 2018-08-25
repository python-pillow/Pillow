# Tests potential DOS of IcnsImagePlugin with 0 length block.
# Run from anywhere that PIL is importable.

from PIL import Image
from PIL._util import py3
from io import BytesIO

if py3:
    Image.open(BytesIO(bytes('icns\x00\x00\x00\x10hang\x00\x00\x00\x00',
                             'latin-1')))
else:
    Image.open(BytesIO(bytes('icns\x00\x00\x00\x10hang\x00\x00\x00\x00')))
