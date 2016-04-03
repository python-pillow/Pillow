from helper import unittest, PillowTestCase
from PIL import Image, PngImagePlugin
from io import BytesIO
import zlib

TEST_FILE = "Tests/images/png_decompression_dos.png"


class TestPngDos(PillowTestCase):
    def test_dos_text(self):

        try:
            im = Image.open(TEST_FILE)
            im.load()
        except ValueError as msg:
            self.assertTrue(msg, "Decompressed Data Too Large")
            return

        for s in im.text.values():
            self.assertLess(len(s), 1024*1024, "Text chunk larger than 1M")

    def test_dos_total_memory(self):
        im = Image.new('L', (1, 1))
        compressed_data = zlib.compress('a'*1024*1023)

        info = PngImagePlugin.PngInfo()

        for x in range(64):
            info.add_text('t%s' % x, compressed_data, 1)
            info.add_itxt('i%s' % x, compressed_data, zip=True)

        b = BytesIO()
        im.save(b, 'PNG', pnginfo=info)
        b.seek(0)

        try:
            im2 = Image.open(b)
        except ValueError as msg:
            self.assertIn("Too much memory", msg)
            return

        total_len = 0
        for txt in im2.text.values():
            total_len += len(txt)
        self.assertLess(total_len, 64*1024*1024,
                        "Total text chunks greater than 64M")

if __name__ == '__main__':
    unittest.main()
