from __future__ import division
from helper import unittest, PillowTestCase
import sys
from PIL import Image
from io import BytesIO

# Limits for testing the leak
mem_limit = 16  # max increase in MB
iterations = 5000
test_file = "Tests/images/hopper.webp"


@unittest.skipIf(sys.platform.startswith('win32'), "requires Unix or MacOS")
class TestWebPLeaks(PillowTestCase):

    def setUp(self):
        try:
            from PIL import _webp
        except ImportError:
            self.skipTest('WebP support not installed')

    def _get_mem_usage(self):
        from resource import getpagesize, getrusage, RUSAGE_SELF
        mem = getrusage(RUSAGE_SELF).ru_maxrss
        return mem * getpagesize() / 1024 / 1024

    def test_leak_load(self):
        with open(test_file, 'rb') as f:
            im_data = f.read()
        start_mem = self._get_mem_usage()
        for _ in range(iterations):
            with Image.open(BytesIO(im_data)) as im:
                im.load()
            mem = (self._get_mem_usage() - start_mem)
            self.assertLess(mem, mem_limit, msg='memory usage limit exceeded')

if __name__ == '__main__':
    unittest.main()
