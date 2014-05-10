#!/usr/bin/env python
#
# The Python Imaging Library
# $Id$
#
# split an animation into a number of frame files
#

from __future__ import print_function

from PIL import Image
import os, sys

class Interval:

    def __init__(self, interval = "0"):

        self.setinterval(interval)

    def setinterval(self, interval):

        self.hilo = []

        for s in interval.split(","):
            if not s.strip():
                continue
            try:
                v = int(s)
                if v < 0:
                    lo, hi = 0, -v
                else:
                    lo = hi = v
            except ValueError:
                i = s.find("-")
                lo, hi = int(s[:i]), int(s[i+1:])

            self.hilo.append((hi, lo))

        if not self.hilo:
            self.hilo = [(sys.maxsize, 0)]

    def __getitem__(self, index):

        for hi, lo in self.hilo:
            if hi >= index >= lo:
                return 1
        return 0

# --------------------------------------------------------------------
# main program

html = 0

if sys.argv[1:2] == ["-h"]:
    html = 1
    del sys.argv[1]

if not sys.argv[2:]:
    print()
    print("Syntax: python explode.py infile template [range]")
    print()
    print("The template argument is used to construct the names of the")
    print("individual frame files.  The frames are numbered file001.ext,")
    print("file002.ext, etc.  You can insert %d to control the placement")
    print("and syntax of the frame number.")
    print()
    print("The optional range argument specifies which frames to extract.")
    print("You can give one or more ranges like 1-10, 5, -15 etc.  If")
    print("omitted, all frames are extracted.")
    sys.exit(1)

infile = sys.argv[1]
outfile = sys.argv[2]

frames = Interval(",".join(sys.argv[3:]))

try:
    # check if outfile contains a placeholder
    outfile % 1
except TypeError:
    file, ext = os.path.splitext(outfile)
    outfile = file + "%03d" + ext

ix = 1

im = Image.open(infile)

if html:
    file, ext = os.path.splitext(outfile)
    html = open(file+".html", "w")
    html.write("<html>\n<body>\n")

while True:

    if frames[ix]:
        im.save(outfile % ix)
        print(outfile % ix)

        if html:
            html.write("<img src='%s'><br>\n" % outfile % ix)

    try:
        im.seek(ix)
    except EOFError:
        break

    ix += 1

if html:
    html.write("</body>\n</html>\n")
