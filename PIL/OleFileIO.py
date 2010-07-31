#
# THIS IS WORK IN PROGRESS
#
# The Python Imaging Library
# $Id$
#
# stuff to deal with OLE2 Structured Storage files.  this module is
# used by PIL to read Image Composer and FlashPix files, but can also
# be used to read other files of this type.
#
# History:
# 1997-01-20 fl   Created
# 1997-01-22 fl   Fixed 64-bit portability quirk
# 2003-09-09 fl   Fixed typo in OleFileIO.loadfat (noted by Daniel Haertle)
# 2004-02-29 fl   Changed long hex constants to signed integers
#
# Notes:
# FIXME: sort out sign problem (eliminate long hex constants)
# FIXME: change filename to use "a/b/c" instead of ["a", "b", "c"]
# FIXME: provide a glob mechanism function (using fnmatchcase)
#
# Literature:
#
# "FlashPix Format Specification, Appendix A", Kodak and Microsoft,
#  September 1996.
#
# Quotes:
#
# "If this document and functionality of the Software conflict,
#  the actual functionality of the Software represents the correct
#  functionality" -- Microsoft, in the OLE format specification
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1997.
#
# See the README file for information on usage and redistribution.
#

import string, StringIO


def i16(c, o = 0):
    return ord(c[o])+(ord(c[o+1])<<8)

def i32(c, o = 0):
    return ord(c[o])+(ord(c[o+1])<<8)+(ord(c[o+2])<<16)+(ord(c[o+3])<<24)


MAGIC = '\320\317\021\340\241\261\032\341'

#
# --------------------------------------------------------------------
# property types

VT_EMPTY=0; VT_NULL=1; VT_I2=2; VT_I4=3; VT_R4=4; VT_R8=5; VT_CY=6;
VT_DATE=7; VT_BSTR=8; VT_DISPATCH=9; VT_ERROR=10; VT_BOOL=11;
VT_VARIANT=12; VT_UNKNOWN=13; VT_DECIMAL=14; VT_I1=16; VT_UI1=17;
VT_UI2=18; VT_UI4=19; VT_I8=20; VT_UI8=21; VT_INT=22; VT_UINT=23;
VT_VOID=24; VT_HRESULT=25; VT_PTR=26; VT_SAFEARRAY=27; VT_CARRAY=28;
VT_USERDEFINED=29; VT_LPSTR=30; VT_LPWSTR=31; VT_FILETIME=64;
VT_BLOB=65; VT_STREAM=66; VT_STORAGE=67; VT_STREAMED_OBJECT=68;
VT_STORED_OBJECT=69; VT_BLOB_OBJECT=70; VT_CF=71; VT_CLSID=72;
VT_VECTOR=0x1000;

# map property id to name (for debugging purposes)

VT = {}
for k, v in vars().items():
    if k[:3] == "VT_":
        VT[v] = k

#
# --------------------------------------------------------------------
# Some common document types (root.clsid fields)

WORD_CLSID = "00020900-0000-0000-C000-000000000046"


#
# --------------------------------------------------------------------

class _OleStream(StringIO.StringIO):

    """OLE2 Stream

    Returns a read-only file object which can be used to read
    the contents of a OLE stream.  To open a stream, use the
    openstream method in the OleFile class.

    This function can be used with either ordinary streams,
    or ministreams, depending on the offset, sectorsize, and
    fat table arguments.
    """

    # FIXME: should store the list of sects obtained by following
    # the fat chain, and load new sectors on demand instead of
    # loading it all in one go.

    def __init__(self, fp, sect, size, offset, sectorsize, fat):

        data = []

        while sect != -2: # 0xFFFFFFFEL:
            fp.seek(offset + sectorsize * sect)
            data.append(fp.read(sectorsize))
            sect = fat[sect]

        data = string.join(data, "")

        # print len(data), size

        StringIO.StringIO.__init__(self, data[:size])

#
# --------------------------------------------------------------------

# FIXME: should add a counter in here to avoid looping forever
# if the tree is broken.

class _OleDirectoryEntry:

    """OLE2 Directory Entry

    Encapsulates a stream directory entry.  Note that the
    constructor builds a tree of all subentries, so we only
    have to call it with the root object.
    """

    def __init__(self, sidlist, sid):

        # store directory parameters.  the caller provides
        # a complete list of directory entries, as read from
        # the directory stream.

        name, type, sect, size, sids, clsid = sidlist[sid]

        self.sid  = sid
        self.name = name
        self.type = type # 1=storage 2=stream
        self.sect = sect
        self.size = size
        self.clsid = clsid

        # process child nodes, if any

        self.kids = []

        sid = sidlist[sid][4][2]

        if sid != -1:

            # the directory entries are organized as a red-black tree.
            # the following piece of code does an ordered traversal of
            # such a tree (at least that's what I hope ;-)

            stack = [self.sid]

            # start at leftmost position

            left, right, child = sidlist[sid][4]

            while left != -1: # 0xFFFFFFFFL:
                stack.append(sid)
                sid = left
                left, right, child = sidlist[sid][4]

            while sid != self.sid:

                self.kids.append(_OleDirectoryEntry(sidlist, sid))

                # try to move right
                left, right, child = sidlist[sid][4]
                if right != -1: # 0xFFFFFFFFL:
                    # and then back to the left
                    sid = right
                    while 1:
                        left, right, child = sidlist[sid][4]
                        if left == -1: # 0xFFFFFFFFL:
                            break
                        stack.append(sid)
                        sid = left
                else:
                    # couldn't move right; move up instead
                    while 1:
                        ptr = stack[-1]
                        del stack[-1]
                        left, right, child = sidlist[ptr][4]
                        if right != sid:
                            break
                        sid = right
                    left, right, child = sidlist[sid][4]
                    if right != ptr:
                        sid = ptr

            # in the OLE file, entries are sorted on (length, name).
            # for convenience, we sort them on name instead.

            self.kids.sort()

    def __cmp__(self, other):
        "Compare entries by name"

        return cmp(self.name, other.name)

    def dump(self, tab = 0):
        "Dump this entry, and all its subentries (for debug purposes only)"

        TYPES = ["(invalid)", "(storage)", "(stream)", "(lockbytes)",
                 "(property)", "(root)"]

        print " "*tab + repr(self.name), TYPES[self.type],
        if self.type in (2, 5):
            print self.size, "bytes",
        print
        if self.type in (1, 5) and self.clsid:
            print " "*tab + "{%s}" % self.clsid

        for kid in self.kids:
            kid.dump(tab + 2)

#
# --------------------------------------------------------------------

##
# This class encapsulates the interface to an OLE 2 structured
# storage file.  Use the {@link listdir} and {@link openstream}
# methods to access the contents of this file.

class OleFileIO:
    """OLE container object

    This class encapsulates the interface to an OLE 2 structured
    storage file.  Use the listdir and openstream methods to access
    the contents of this file.

    Object names are given as a list of strings, one for each subentry
    level.  The root entry should be omitted.  For example, the following
    code extracts all image streams from a Microsoft Image Composer file:

        ole = OleFileIO("fan.mic")

        for entry in ole.listdir():
            if entry[1:2] == "Image":
                fin = ole.openstream(entry)
                fout = open(entry[0:1], "wb")
                while 1:
                    s = fin.read(8192)
                    if not s:
                        break
                    fout.write(s)

    You can use the viewer application provided with the Python Imaging
    Library to view the resulting files (which happens to be standard
    TIFF files).
    """

    def __init__(self, filename = None):

        if filename:
            self.open(filename)

    ##
    # Open an OLE2 file.

    def open(self, filename):
        """Open an OLE2 file"""

        if type(filename) == type(""):
            self.fp = open(filename, "rb")
        else:
            self.fp = filename

        header = self.fp.read(512)

        if len(header) != 512 or header[:8] != MAGIC:
            raise IOError, "not an OLE2 structured storage file"

        # file clsid (probably never used, so we don't store it)
        clsid = self._clsid(header[8:24])

        # FIXME: could check version and byte order fields

        self.sectorsize = 1 << i16(header, 30)
        self.minisectorsize = 1 << i16(header, 32)

        self.minisectorcutoff = i32(header, 56)

        # Load file allocation tables
        self.loadfat(header)

        # Load direcory.  This sets both the sidlist (ordered by id)
        # and the root (ordered by hierarchy) members.
        self.loaddirectory(i32(header, 48))

        self.ministream = None
        self.minifatsect = i32(header, 60)

    def loadfat(self, header):
        # Load the FAT table.  The header contains a sector numbers
        # for the first 109 FAT sectors.  Additional sectors are
        # described by DIF blocks (FIXME: not yet implemented)

        sect = header[76:512]
        fat = []
        for i in range(0, len(sect), 4):
            ix = i32(sect, i)
            if ix == -2 or ix == -1: # ix == 0xFFFFFFFEL or ix == 0xFFFFFFFFL:
                break
            s = self.getsect(ix)
            fat = fat + map(lambda i, s=s: i32(s, i), range(0, len(s), 4))
        self.fat = fat

    def loadminifat(self):
        # Load the MINIFAT table.  This is stored in a standard sub-
        # stream, pointed to by a header field.

        s = self._open(self.minifatsect).read()

        self.minifat = map(lambda i, s=s: i32(s, i), range(0, len(s), 4))

    def getsect(self, sect):
        # Read given sector

        self.fp.seek(512 + self.sectorsize * sect)
        return self.fp.read(self.sectorsize)

    def _unicode(self, s):
        # Map unicode string to Latin 1

        # FIXME: some day, Python will provide an official way to handle
        # Unicode strings, but until then, this will have to do...
        return filter(ord, s)

    def loaddirectory(self, sect):
        # Load the directory.  The directory is stored in a standard
        # substream, independent of its size.

        # read directory stream
        fp = self._open(sect)

        # create list of sid entries
        self.sidlist = []
        while 1:
            entry = fp.read(128)
            if not entry:
                break
            type = ord(entry[66])
            name = self._unicode(entry[0:0+i16(entry, 64)])
            ptrs = i32(entry, 68), i32(entry, 72), i32(entry, 76)
            sect, size = i32(entry, 116), i32(entry, 120)
            clsid = self._clsid(entry[80:96])
            self.sidlist.append((name, type, sect, size, ptrs, clsid))

        # create hierarchical list of directory entries
        self.root = _OleDirectoryEntry(self.sidlist, 0)

    def dumpdirectory(self):
        # Dump directory (for debugging only)

        self.root.dump()

    def _clsid(self, clsid):
        if clsid == "\0" * len(clsid):
            return ""
        return (("%08X-%04X-%04X-%02X%02X-" + "%02X" * 6) %
                ((i32(clsid, 0), i16(clsid, 4), i16(clsid, 6)) +
                tuple(map(ord, clsid[8:16]))))

    def _list(self, files, prefix, node):
        # listdir helper

        prefix = prefix + [node.name]
        for entry in node.kids:
            if entry.kids:
                self._list(files, prefix, entry)
            else:
                files.append(prefix[1:] + [entry.name])

    def _find(self, filename):
        # openstream helper

        node = self.root
        for name in filename:
            for kid in node.kids:
                if kid.name == name:
                    break
            else:
                raise IOError, "file not found"
            node = kid
        return node.sid

    def _open(self, start, size = 0x7FFFFFFF):
        # openstream helper.

        if size < self.minisectorcutoff:
            # ministream object
            if not self.ministream:
                self.loadminifat()
                self.ministream = self._open(self.sidlist[0][2])
            return _OleStream(self.ministream, start, size, 0,
                              self.minisectorsize, self.minifat)

        # standard stream
        return _OleStream(self.fp, start, size, 512,
                          self.sectorsize, self.fat)

    ##
    # Returns a list of streams stored in this file.

    def listdir(self):
        """Return a list of streams stored in this file"""

        files = []
        self._list(files, [], self.root)
        return files

    ##
    # Opens a stream as a read-only file object.

    def openstream(self, filename):
        """Open a stream as a read-only file object"""

        slot = self._find(filename)
        name, type, sect, size, sids, clsid = self.sidlist[slot]
        if type != 2:
            raise IOError, "this file is not a stream"
        return self._open(sect, size)

    ##
    # Gets a list of properties described in substream.

    def getproperties(self, filename):
        """Return properties described in substream"""

        fp = self.openstream(filename)

        data = {}

        # header
        s = fp.read(28)
        clsid = self._clsid(s[8:24])

        # format id
        s = fp.read(20)
        fmtid = self._clsid(s[:16])
        fp.seek(i32(s, 16))

        # get section
        s = "****" + fp.read(i32(fp.read(4))-4)

        for i in range(i32(s, 4)):

            id = i32(s, 8+i*8)
            offset = i32(s, 12+i*8)
            type = i32(s, offset)

            # test for common types first (should perhaps use
            # a dictionary instead?)

            if type == VT_I2:
                value = i16(s, offset+4)
                if value >= 32768:
                    value = value - 65536
            elif type == VT_UI2:
                value = i16(s, offset+4)
            elif type in (VT_I4, VT_ERROR):
                value = i32(s, offset+4)
            elif type == VT_UI4:
                value = i32(s, offset+4) # FIXME
            elif type in (VT_BSTR, VT_LPSTR):
                count = i32(s, offset+4)
                value = s[offset+8:offset+8+count-1]
            elif type == VT_BLOB:
                count = i32(s, offset+4)
                value = s[offset+8:offset+8+count]
            elif type == VT_LPWSTR:
                count = i32(s, offset+4)
                value = self._unicode(s[offset+8:offset+8+count*2])
            elif type == VT_FILETIME:
                value = long(i32(s, offset+4)) + (long(i32(s, offset+8))<<32)
                # FIXME: this is a 64-bit int: "number of 100ns periods
                # since Jan 1,1601".  Should map this to Python time
                value = value / 10000000L # seconds
            elif type == VT_UI1:
                value = ord(s[offset+4])
            elif type == VT_CLSID:
                value = self._clsid(s[offset+4:offset+20])
            elif type == VT_CF:
                count = i32(s, offset+4)
                value = s[offset+8:offset+8+count]
            else:
                value = None # everything else yields "None"

            # FIXME: add support for VT_VECTOR

            #print "%08x" % id, repr(value),
            #print "(%s)" % VT[i32(s, offset) & 0xFFF]

            data[id] = value

        return data

#
# --------------------------------------------------------------------
# This script can be used to dump the directory of any OLE2 structured
# storage file.

if __name__ == "__main__":

    import sys

    for file in sys.argv[1:]:
        try:
            ole = OleFileIO(file)
            print "-" * 68
            print file
            print "-" * 68
            ole.dumpdirectory()
            for file in ole.listdir():
                if file[-1][0] == "\005":
                    print file
                    props = ole.getproperties(file)
                    props = props.items()
                    props.sort()
                    for k, v in props:
                        print "   ", k, v
        except IOError, v:
            print "***", "cannot read", file, "-", v
