#
# The Python Imaging Library
# $Id$
#
# simple postscript graphics interface
#
# History:
# 1996-04-20 fl   Created
# 1999-01-10 fl   Added gsave/grestore to image method
# 2005-05-04 fl   Fixed floating point issue in image (from Eric Etheridge)
#
# Copyright (c) 1997-2005 by Secret Labs AB.  All rights reserved.
# Copyright (c) 1996 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

import EpsImagePlugin
import string

##
# Simple Postscript graphics interface.

class PSDraw:

    def __init__(self, fp=None):
        if not fp:
            import sys
            fp = sys.stdout
        self.fp = fp

    def begin_document(self, id = None):
        "Write Postscript DSC header"
        # FIXME: incomplete
        self.fp.write("%!PS-Adobe-3.0\n"
                      "save\n"
                      "/showpage { } def\n"
                      "%%EndComments\n"
                      "%%BeginDocument\n")
        #self.fp.write(ERROR_PS) # debugging!
        self.fp.write(EDROFF_PS)
        self.fp.write(VDI_PS)
        self.fp.write("%%EndProlog\n")
        self.isofont = {}

    def end_document(self):
        "Write Postscript DSC footer"
        self.fp.write("%%EndDocument\n"
                      "restore showpage\n"
                      "%%End\n")
        if hasattr(self.fp, "flush"):
            self.fp.flush()

    def setfont(self, font, size):
        if not self.isofont.has_key(font):
            # reencode font
            self.fp.write("/PSDraw-%s ISOLatin1Encoding /%s E\n" %\
                          (font, font))
            self.isofont[font] = 1
        # rough
        self.fp.write("/F0 %d /PSDraw-%s F\n" % (size, font))

    def setink(self, ink):
        print "*** NOT YET IMPLEMENTED ***"

    def line(self, xy0, xy1):
        xy = xy0 + xy1
        self.fp.write("%d %d %d %d Vl\n" % xy)

    def rectangle(self, box):
        self.fp.write("%d %d M %d %d 0 Vr\n" % box)

    def text(self, xy, text):
        text = string.joinfields(string.splitfields(text, "("), "\\(")
        text = string.joinfields(string.splitfields(text, ")"), "\\)")
        xy = xy + (text,)
        self.fp.write("%d %d M (%s) S\n" % xy)

    def image(self, box, im, dpi = None):
        "Write an PIL image"
        # default resolution depends on mode
        if not dpi:
            if im.mode == "1":
                dpi = 200 # fax
            else:
                dpi = 100 # greyscale
        # image size (on paper)
        x = float(im.size[0] * 72) / dpi
        y = float(im.size[1] * 72) / dpi
        # max allowed size
        xmax = float(box[2] - box[0])
        ymax = float(box[3] - box[1])
        if x > xmax:
            y = y * xmax / x; x = xmax
        if y > ymax:
            x = x * ymax / y; y = ymax
        dx = (xmax - x) / 2 + box[0]
        dy = (ymax - y) / 2 + box[1]
        self.fp.write("gsave\n%f %f translate\n" % (dx, dy))
        if (x, y) != im.size:
            # EpsImagePlugin._save prints the image at (0,0,xsize,ysize)
            sx = x / im.size[0]
            sy = y / im.size[1]
            self.fp.write("%f %f scale\n" % (sx, sy))
        EpsImagePlugin._save(im, self.fp, None, 0)
        self.fp.write("\ngrestore\n")

# --------------------------------------------------------------------
# Postscript driver

#
# EDROFF.PS -- Postscript driver for Edroff 2
#
# History:
# 94-01-25 fl: created (edroff 2.04)
#
# Copyright (c) Fredrik Lundh 1994.
#

EDROFF_PS = """\
/S { show } bind def
/P { moveto show } bind def
/M { moveto } bind def
/X { 0 rmoveto } bind def
/Y { 0 exch rmoveto } bind def
/E {    findfont
        dup maxlength dict begin
        {
                1 index /FID ne { def } { pop pop } ifelse
        } forall
        /Encoding exch def
        dup /FontName exch def
        currentdict end definefont pop
} bind def
/F {    findfont exch scalefont dup setfont
        [ exch /setfont cvx ] cvx bind def
} bind def
"""

#
# VDI.PS -- Postscript driver for VDI meta commands
#
# History:
# 94-01-25 fl: created (edroff 2.04)
#
# Copyright (c) Fredrik Lundh 1994.
#

VDI_PS = """\
/Vm { moveto } bind def
/Va { newpath arcn stroke } bind def
/Vl { moveto lineto stroke } bind def
/Vc { newpath 0 360 arc closepath } bind def
/Vr {   exch dup 0 rlineto
        exch dup neg 0 exch rlineto
        exch neg 0 rlineto
        0 exch rlineto
        100 div setgray fill 0 setgray } bind def
/Tm matrix def
/Ve {   Tm currentmatrix pop
        translate scale newpath 0 0 .5 0 360 arc closepath
        Tm setmatrix
} bind def
/Vf { currentgray exch setgray fill setgray } bind def
"""

#
# ERROR.PS -- Error handler
#
# History:
# 89-11-21 fl: created (pslist 1.10)
#

ERROR_PS = """\
/landscape false def
/errorBUF 200 string def
/errorNL { currentpoint 10 sub exch pop 72 exch moveto } def
errordict begin /handleerror {
    initmatrix /Courier findfont 10 scalefont setfont
    newpath 72 720 moveto $error begin /newerror false def
    (PostScript Error) show errorNL errorNL
    (Error: ) show
        /errorname load errorBUF cvs show errorNL errorNL
    (Command: ) show
        /command load dup type /stringtype ne { errorBUF cvs } if show
        errorNL errorNL
    (VMstatus: ) show
        vmstatus errorBUF cvs show ( bytes available, ) show
        errorBUF cvs show ( bytes used at level ) show
        errorBUF cvs show errorNL errorNL
    (Operand stargck: ) show errorNL /ostargck load {
        dup type /stringtype ne { errorBUF cvs } if 72 0 rmoveto show errorNL
    } forall errorNL
    (Execution stargck: ) show errorNL /estargck load {
        dup type /stringtype ne { errorBUF cvs } if 72 0 rmoveto show errorNL
    } forall
    end showpage
} def end
"""
