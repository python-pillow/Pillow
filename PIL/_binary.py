#
# The Python Imaging Library.
# $Id$
#
# Binary input/output support routines.
#
# Copyright (c) 1997-2003 by Secret Labs AB
# Copyright (c) 1995-2003 by Fredrik Lundh
# Copyright (c) 2012 by Brian Crowell
#
# See the README file for information on usage and redistribution.
#

if bytes is str:
    def i8(c):
        return ord(c)

    def o8(i):
        return chr(i & 255)
else:
    def i8(c):
        return c if c.__class__ is int else c[0]

    def o8(i):
        return bytes((i & 255,))


# Input, le = little endian, be = big endian
# TODO: replace with more readable struct.unpack equivalent
def i16le(c, o=0):
    """
    Converts a 2-bytes (16 bits) string to an integer.

    c: string containing bytes to convert
    o: offset of bytes to convert in string
    """
    return i8(c[o]) | (i8(c[o+1]) << 8)


def i32le(c, o=0):
    """
    Converts a 4-bytes (32 bits) string to an integer.

    c: string containing bytes to convert
    o: offset of bytes to convert in string
    """
    return (i8(c[o]) | (i8(c[o+1]) << 8) | (i8(c[o+2]) << 16) |
            (i8(c[o+3]) << 24))


def i16be(c, o=0):
    return (i8(c[o]) << 8) | i8(c[o+1])


def i32be(c, o=0):
    return ((i8(c[o]) << 24) | (i8(c[o+1]) << 16) |
            (i8(c[o+2]) << 8) | i8(c[o+3]))


# Output, le = little endian, be = big endian
def o16le(i):
    return o8(i) + o8(i >> 8)


def o32le(i):
    return o8(i) + o8(i >> 8) + o8(i >> 16) + o8(i >> 24)


def o16be(i):
    return o8(i >> 8) + o8(i)


def o32be(i):
    return o8(i >> 24) + o8(i >> 16) + o8(i >> 8) + o8(i)

# End of file
