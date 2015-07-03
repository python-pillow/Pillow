#!/usr/bin/env python

from __future__ import division
from helper import unittest, PillowTestCase
import sys
from PIL import Image

min_iterations = 100
max_iterations = 10000


@unittest.skipIf(sys.platform.startswith('win32'), "requires Unix or MacOS")
class TestImagingLeaks(PillowTestCase):

    def _get_mem_usage(self):
        from resource import getpagesize, getrusage, RUSAGE_SELF
        mem = getrusage(RUSAGE_SELF).ru_maxrss
        return mem * getpagesize() / 1024 / 1024

    def _test_leak(self, min_iterations, max_iterations, fn, *args, **kwargs):
        mem_limit = None
        for i in range(max_iterations):
            fn(*args, **kwargs)
            mem = self._get_mem_usage()
            if i < min_iterations:
                mem_limit = mem + 1
                continue
            self.assertLessEqual(mem, mem_limit,
                                 msg='memory usage limit exceeded after %d iterations'
                                 % (i + 1))

    def test_leak_putdata(self):
        im = Image.new('RGB', (25, 25))
        self._test_leak(min_iterations, max_iterations,
                        im.putdata, im.getdata())

    def test_leak_getlist(self):
        im = Image.new('P', (25, 25))
        self._test_leak(min_iterations, max_iterations,
                        # Pass a new list at each iteration.
                        lambda: im.point(range(256)))

if __name__ == '__main__':
    unittest.main()
