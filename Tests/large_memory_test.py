from helper import *

# This test is not run automatically.
#
# It requires > 2gb memory for the >2 gigapixel image generated in the
# second test.  Running this automatically would amount to a denial of
# service on our testing infrastructure.  I expect this test to fail
# on any 32 bit machine, as well as any smallish things (like
# Raspberry Pis). It does succeed on a 3gb Ubuntu 12.04x64 VM on Python
# 2.7 an 3.2.

from PIL import Image
YDIM = 32769
XDIM = 48000


class LargeMemoryTest(PillowTestCase):

    def _write_png(self, XDIM, YDIM):
        f = self.tempfile('temp.png')
        im = Image.new('L', (XDIM, YDIM), (0))
        im.save(f)

    def test_large(self):
        """ succeeded prepatch"""
        self._write_png(XDIM, YDIM)

    def test_2gpx(self):
        """failed prepatch"""
        self._write_png(XDIM, YDIM)


if __name__ == '__main__':
    unittest.main()

# End of file
