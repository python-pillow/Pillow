#
# The Python Imaging Library
# $Id$
#
# bitmap distribution font (bdf) file parser
#
# history:
# 1996-05-16 fl   created (as bdf2pil)
# 1997-08-25 fl   converted to FontFile driver
# 2001-05-25 fl   removed bogus __init__ call
# 2002-11-20 fl   robustification (from Kevin Cazabon, Dmitry Vasiliev)
# 2003-04-22 fl   more robustification (from Graham Dumpleton)
#
# Copyright (c) 1997-2003 by Secret Labs AB.
# Copyright (c) 1997-2003 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

import Image
import FontFile

import string

# --------------------------------------------------------------------
# parse X Bitmap Distribution Format (BDF)
# --------------------------------------------------------------------

bdf_slant = {
   "R": "Roman",
   "I": "Italic",
   "O": "Oblique",
   "RI": "Reverse Italic",
   "RO": "Reverse Oblique",
   "OT": "Other"
}

bdf_spacing = {
    "P": "Proportional",
    "M": "Monospaced",
    "C": "Cell"
}

def bdf_char(f):

    # skip to STARTCHAR
    while 1:
        s = f.readline()
        if not s:
            return None
        if s[:9] == "STARTCHAR":
            break
    id = string.strip(s[9:])

    # load symbol properties
    props = {}
    while 1:
        s = f.readline()
        if not s or s[:6] == "BITMAP":
            break
        i = string.find(s, " ")
        props[s[:i]] = s[i+1:-1]

    # load bitmap
    bitmap = []
    while 1:
        s = f.readline()
        if not s or s[:7] == "ENDCHAR":
            break
        bitmap.append(s[:-1])
    bitmap = string.join(bitmap, "")

    [x, y, l, d] = map(int, string.split(props["BBX"]))
    [dx, dy] = map(int, string.split(props["DWIDTH"]))

    bbox = (dx, dy), (l, -d-y, x+l, -d), (0, 0, x, y)

    try:
        im = Image.fromstring("1", (x, y), bitmap, "hex", "1")
    except ValueError:
        # deal with zero-width characters
        im = Image.new("1", (x, y))

    return id, int(props["ENCODING"]), bbox, im

##
# Font file plugin for the X11 BDF format.

class BdfFontFile(FontFile.FontFile):

    def __init__(self, fp):

        FontFile.FontFile.__init__(self)

        s = fp.readline()
        if s[:13] != "STARTFONT 2.1":
            raise SyntaxError, "not a valid BDF file"

        props = {}
        comments = []

        while 1:
            s = fp.readline()
            if not s or s[:13] == "ENDPROPERTIES":
                break
            i = string.find(s, " ")
            props[s[:i]] = s[i+1:-1]
            if s[:i] in ["COMMENT", "COPYRIGHT"]:
                if string.find(s, "LogicalFontDescription") < 0:
                    comments.append(s[i+1:-1])

        font = string.split(props["FONT"], "-")

        font[4] = bdf_slant[string.upper(font[4])]
        font[11] = bdf_spacing[string.upper(font[11])]

        ascent = int(props["FONT_ASCENT"])
        descent = int(props["FONT_DESCENT"])

        fontname = string.join(font[1:], ";")

        # print "#", fontname
        # for i in comments:
        #       print "#", i

        font = []
        while 1:
            c = bdf_char(fp)
            if not c:
                break
            id, ch, (xy, dst, src), im = c
            if ch >= 0 and ch < len(self.glyph):
                self.glyph[ch] = xy, dst, src, im
