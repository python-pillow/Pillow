import zlib
from io import BytesIO

from PIL import Image, ImageFile, PngImagePlugin

TEST_FILE = "Tests/images/png_decompression_dos.png"


def test_ignore_dos_text():
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    try:
        im = Image.open(TEST_FILE)
        im.load()
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False

    for s in im.text.values():
        assert len(s) < 1024 * 1024, "Text chunk larger than 1M"

    for s in im.info.values():
        assert len(s) < 1024 * 1024, "Text chunk larger than 1M"


def test_dos_text():

    try:
        im = Image.open(TEST_FILE)
        im.load()
    except ValueError as msg:
        assert msg, "Decompressed Data Too Large"
        return

    for s in im.text.values():
        assert len(s) < 1024 * 1024, "Text chunk larger than 1M"


def test_dos_total_memory():
    im = Image.new("L", (1, 1))
    compressed_data = zlib.compress(b"a" * 1024 * 1023)

    info = PngImagePlugin.PngInfo()

    for x in range(64):
        info.add_text(f"t{x}", compressed_data, zip=True)
        info.add_itxt(f"i{x}", compressed_data, zip=True)

    b = BytesIO()
    im.save(b, "PNG", pnginfo=info)
    b.seek(0)

    try:
        im2 = Image.open(b)
    except ValueError as msg:
        assert "Too much memory" in msg
        return

    total_len = 0
    for txt in im2.text.values():
        total_len += len(txt)
    assert total_len < 64 * 1024 * 1024, "Total text chunks greater than 64M"
