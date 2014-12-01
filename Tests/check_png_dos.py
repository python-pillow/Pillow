from helper import unittest, PillowTestCase
import sys
from PIL import Image
from io import BytesIO

test_file = "Tests/images/png_decompression_dos.png"

@unittest.skipIf(sys.platform.startswith('win32'), "requires Unix or MacOS")
class TestPngDos(PillowTestCase):

    def test_dos_text(self):

        try:
            im = Image.open(test_file)
            im.load()
        except ValueError as msg:
            self.assert_(msg, "Decompressed Data Too Large")
            return

        for s in im.text.values():
            self.assert_(len(s) < 1024*1024, "Text chunk larger than 1M")

if __name__ == '__main__':
    unittest.main()
