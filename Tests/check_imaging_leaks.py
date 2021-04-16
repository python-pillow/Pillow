#!/usr/bin/env python3
import pytest

from PIL import Image

from .helper import is_win32

min_iterations = 100
max_iterations = 10000

pytestmark = pytest.mark.skipif(is_win32(), reason="requires Unix or macOS")


def _get_mem_usage():
    from resource import RUSAGE_SELF, getpagesize, getrusage

    mem = getrusage(RUSAGE_SELF).ru_maxrss
    return mem * getpagesize() / 1024 / 1024


def _test_leak(min_iterations, max_iterations, fn, *args, **kwargs):
    mem_limit = None
    for i in range(max_iterations):
        fn(*args, **kwargs)
        mem = _get_mem_usage()
        if i < min_iterations:
            mem_limit = mem + 1
            continue
        msg = f"memory usage limit exceeded after {i + 1} iterations"
        assert mem <= mem_limit, msg


def test_leak_putdata():
    im = Image.new("RGB", (25, 25))
    _test_leak(min_iterations, max_iterations, im.putdata, im.getdata())


def test_leak_getlist():
    im = Image.new("P", (25, 25))
    _test_leak(
        min_iterations,
        max_iterations,
        # Pass a new list at each iteration.
        lambda: im.point(range(256)),
    )
