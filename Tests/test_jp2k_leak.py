from helper import unittest, PillowTestCase, tearDownModule
import sys

from PIL import Image
from resource import setrlimit, RLIMIT_AS, RLIMIT_STACK

# Limits for testing the leak
mem_limit = 512*1048576
stack_size = 8*1048576
iterations = (mem_limit/stack_size)*2
codecs = dir(Image.core)
test_file = "Tests/images/rgb_trns_ycbc.jp2"

@unittest.skipIf(sys.platform.startswith('win32'), "requires Unix or MacOS")
class TestJp2kLeak(PillowTestCase):
    def setUp(self):
        if "jpeg2k_encoder" not in codecs or "jpeg2k_decoder" not in codecs:
            self.skipTest('JPEG 2000 support not available')

    def test_leak(self):
        setrlimit(RLIMIT_STACK, (stack_size, stack_size))
        setrlimit(RLIMIT_AS, (mem_limit, mem_limit))
        for count in range(iterations):
            with Image.open(test_file) as im:
                im.load()
                im.close()


if __name__ == '__main__':
    unittest.main()
