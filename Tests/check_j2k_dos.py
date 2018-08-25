# Tests potential DOS of Jpeg2kImagePlugin with 0 length block.
# Run from anywhere that PIL is importable.

from PIL import Image
from PIL._util import py3
from io import BytesIO

if py3:
    Image.open(BytesIO(bytes(
        '\x00\x00\x00\x0cjP\x20\x20\x0d\x0a\x87\x0a\x00\x00\x00\x00hang',
        'latin-1')))

else:
    Image.open(BytesIO(bytes(
        '\x00\x00\x00\x0cjP\x20\x20\x0d\x0a\x87\x0a\x00\x00\x00\x00hang')))
