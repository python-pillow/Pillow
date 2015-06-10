#!/usr/bin/env python
#
# The Python Imaging Library.
# $Id$
#
# convert image files
#
# History:
# 0.1   96-04-20 fl     Created
# 0.2   96-10-04 fl     Use draft mode when converting images
# 0.3   96-12-30 fl     Optimize output (PNG, JPEG)
# 0.4   97-01-18 fl     Made optimize an option (PNG, JPEG)
# 0.5   98-12-30 fl     Fixed -f option (from Anthony Baxter)
#

from __future__ import print_function

import getopt
import string
import sys

from PIL import Image


def usage():
    print("PIL Convert 0.5/1998-12-30 -- convert image files")
    print("Usage: pilconvert [option] infile outfile")
    print()
    print("Options:")
    print()
    print("  -c <format>  convert to format (default is given by extension)")
    print()
    print("  -g           convert to greyscale")
    print("  -p           convert to palette image (using standard palette)")
    print("  -r           convert to rgb")
    print()
    print("  -o           optimize output (trade speed for size)")
    print("  -q <value>   set compression quality (0-100, JPEG only)")
    print()
    print("  -f           list supported file formats")
    sys.exit(1)

if len(sys.argv) == 1:
    usage()

try:
    opt, argv = getopt.getopt(sys.argv[1:], "c:dfgopq:r")
except getopt.error as v:
    print(v)
    sys.exit(1)

output_format = None
convert = None

options = {}

for o, a in opt:

    if o == "-f":
        Image.init()
        id = sorted(Image.ID)
        print("Supported formats (* indicates output format):")
        for i in id:
            if i in Image.SAVE:
                print(i+"*", end=' ')
            else:
                print(i, end=' ')
        sys.exit(1)

    elif o == "-c":
        output_format = a

    if o == "-g":
        convert = "L"
    elif o == "-p":
        convert = "P"
    elif o == "-r":
        convert = "RGB"

    elif o == "-o":
        options["optimize"] = 1
    elif o == "-q":
        options["quality"] = string.atoi(a)

if len(argv) != 2:
    usage()

try:
    im = Image.open(argv[0])
    if convert and im.mode != convert:
        im.draft(convert, im.size)
        im = im.convert(convert)
    if output_format:
        im.save(argv[1], output_format, **options)
    else:
        im.save(argv[1], **options)
except:
    print("cannot convert image", end=' ')
    print("(%s:%s)" % (sys.exc_info()[0], sys.exc_info()[1]))
