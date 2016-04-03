#
# The Python Imaging Library.
# $Id$
#
# a class to read from a container file
#
# History:
# 1995-06-18 fl     Created
# 1995-09-07 fl     Added readline(), readlines()
#
# Copyright (c) 1997-2001 by Secret Labs AB
# Copyright (c) 1995 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

##
# A file object that provides read access to a part of an existing
# file (for example a TAR file).


class ContainerIO(object):

    ##
    # Create file object.
    #
    # @param file Existing file.
    # @param offset Start of region, in bytes.
    # @param length Size of region, in bytes.

    def __init__(self, file, offset, length):
        self.fh = file
        self.pos = 0
        self.offset = offset
        self.length = length
        self.fh.seek(offset)

    ##
    # Always false.

    def isatty(self):
        return 0

    ##
    # Move file pointer.
    #
    # @param offset Offset in bytes.
    # @param mode Starting position. Use 0 for beginning of region, 1
    #    for current offset, and 2 for end of region.  You cannot move
    #    the pointer outside the defined region.

    def seek(self, offset, mode=0):
        if mode == 1:
            self.pos = self.pos + offset
        elif mode == 2:
            self.pos = self.length + offset
        else:
            self.pos = offset
        # clamp
        self.pos = max(0, min(self.pos, self.length))
        self.fh.seek(self.offset + self.pos)

    ##
    # Get current file pointer.
    #
    # @return Offset from start of region, in bytes.

    def tell(self):
        return self.pos

    ##
    # Read data.
    #
    # @def read(bytes=0)
    # @param bytes Number of bytes to read.  If omitted or zero,
    #     read until end of region.
    # @return An 8-bit string.

    def read(self, n=0):
        if n:
            n = min(n, self.length - self.pos)
        else:
            n = self.length - self.pos
        if not n:  # EOF
            return ""
        self.pos = self.pos + n
        return self.fh.read(n)

    ##
    # Read a line of text.
    #
    # @return An 8-bit string.

    def readline(self):
        s = ""
        while True:
            c = self.read(1)
            if not c:
                break
            s = s + c
            if c == "\n":
                break
        return s

    ##
    # Read multiple lines of text.
    #
    # @return A list of 8-bit strings.

    def readlines(self):
        l = []
        while True:
            s = self.readline()
            if not s:
                break
            l.append(s)
        return l
