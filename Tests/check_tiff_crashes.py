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


import io
import zipfile

from PIL import Image

# The vulnerabilities represented by these files have been addressed.
# However, antivirus software does not detect that this is a version of Pillow
# with those fixes, and so to prevent unnecessary alarm, the files are
# hidden inside a password-protected zip
repro_read_strip = (
    "crash_1.tif",
    "crash_2.tif",
)

with zipfile.ZipFile("images/crash.zip") as crashzip:
    for path in repro_read_strip:
        with crashzip.open(path, pwd=b"vulnerabilitiesaddressed") as f:
            data = io.BytesIO(f.read())
        with Image.open(data) as im:
            try:
                im.load()
            except Exception as msg:
                print(msg)
