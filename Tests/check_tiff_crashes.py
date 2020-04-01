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


from PIL import Image

repro_read_strip = (
    "images/crash_1.tif",
    "images/crash_2.tif",
)

for path in repro_read_strip:
    with Image.open(path) as im:
        try:
            im.load()
        except Exception as msg:
            print(msg)
