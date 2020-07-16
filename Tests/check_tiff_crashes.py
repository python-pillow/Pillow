#!/usr/bin/env python

# Reproductions/tests for crashes/read errors in TiffDecode.c

# When run in python, all of these images should fail for
# one reason or another, either as a buffer overrun,
# unrecognized datastream, or truncated image file.
# There shouldn't be any segfaults.
#
# if run like
# `valgrind --tool=memcheck python check_tiff_crashes.py  2>&1 | grep TiffDecode.c`
# the output should be empty. There may be python issues
# in the valgrind especially if run in a debug python
# version.


import urllib.request

from PIL import Image

repro_read_strip = (
    "crash_1.tif",
    "crash_2.tif",
)

for path in repro_read_strip:
    repo = "https://raw.githubusercontent.com/python-pillow/Pillow/master/"
    with urllib.request.urlopen(repo + "Tests/images/" + path) as f:
        with Image.open(f) as im:
            try:
                im.load()
            except Exception as msg:
                print(msg)
