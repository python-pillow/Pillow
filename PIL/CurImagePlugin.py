#
# The Python Imaging Library.
# $Id$
#
# Windows Cursor support for PIL
#
# notes:
#       uses BmpImagePlugin.py to read the bitmap data.
#
# history:
#       96-05-27 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.1"

import Image, BmpImagePlugin


#
# --------------------------------------------------------------------

def i16(c):
    return ord(c[0]) + (ord(c[1])<<8)

def i32(c):
    return ord(c[0]) + (ord(c[1])<<8) + (ord(c[2])<<16) + (ord(c[3])<<24)


def _accept(prefix):
    return prefix[:4] == "\0\0\2\0"

##
# Image plugin for Windows Cursor files.

class CurImageFile(BmpImagePlugin.BmpImageFile):

    format = "CUR"
    format_description = "Windows Cursor"

    def _open(self):

        offset = self.fp.tell()

        # check magic
        s = self.fp.read(6)
        if not _accept(s):
            raise SyntaxError, "not an CUR file"

        # pick the largest cursor in the file
        m = ""
        for i in range(i16(s[4:])):
            s = self.fp.read(16)
            if not m:
                m = s
            elif ord(s[0]) > ord(m[0]) and ord(s[1]) > ord(m[1]):
                m = s
            #print "width", ord(s[0])
            #print "height", ord(s[1])
            #print "colors", ord(s[2])
            #print "reserved", ord(s[3])
            #print "hotspot x", i16(s[4:])
            #print "hotspot y", i16(s[6:])
            #print "bytes", i32(s[8:])
            #print "offset", i32(s[12:])

        # load as bitmap
        self._bitmap(i32(m[12:]) + offset)

        # patch up the bitmap height
        self.size = self.size[0], self.size[1]/2
        d, e, o, a = self.tile[0]
        self.tile[0] = d, (0,0)+self.size, o, a

        return


#
# --------------------------------------------------------------------

Image.register_open("CUR", CurImageFile, _accept)

Image.register_extension("CUR", ".cur")
