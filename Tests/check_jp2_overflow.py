#!/usr/bin/env python3

# Reproductions/tests for OOB read errors in FliDecode.c

# When run in python, all of these images should fail for
# one reason or another, either as a buffer overrun,
# unrecognized datastream, or truncated image file.
# There shouldn't be any segfaults.
#
# if run like
# `valgrind --tool=memcheck python check_jp2_overflow.py  2>&1 | grep Decode.c`
# the output should be empty. There may be python issues
# in the valgrind especially if run in a debug python
# version.


from PIL import Image

repro = ("00r0_gray_l.jp2", "00r1_graya_la.jp2")

for path in repro:
    im = Image.open(path)
    try:
        im.load()
    except Exception as msg:
        print(msg)
