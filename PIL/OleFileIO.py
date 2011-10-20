#!/usr/local/bin/python
# -*- coding: latin-1 -*-
"""
OleFileIO_PL:
    Module to read Microsoft OLE2 files (Structured Storage), such as
    Microsoft Office documents, Image Composer and FlashPix files,
    Outlook messages, ...

version 0.13 2007-09-04 Philippe Lagadec - http://lagasoft.free.fr

Improved version of OleFileIO module from PIL library v1.1.6
See: http://www.pythonware.com/products/pil/index.htm

The Python Imaging Library (PIL) is
    Copyright (c) 1997-2005 by Secret Labs AB
    Copyright (c) 1995-2005 by Fredrik Lundh
OleFileIO_PL changes are Copyright (c) 2005-2007 by Philippe Lagadec

See source code and LICENSE.txt for information on usage and redistribution.

WARNING: THIS IS (STILL) WORK IN PROGRESS.
"""

__author__  = "Fredrik Lundh (Secret Labs AB), Philippe Lagadec"
__date__    = "2007-09-04"
__version__ = '0.13'

#-----------------------------------------------------------------------------
# CHANGELOG: (OleFileIO_PL changes only)
# 2005-05-11 v0.10 PL: - a few fixes for Python 2.4 compatibility
#                        (all changes flagged with [PL])
# 2006-02-22 v0.11 PL: - a few fixes for some Office 2003 documents which raise
#                        exceptions in _OleStream.__init__()
# 2006-06-09 v0.12 PL: - fixes for files above 6.8MB (DIFAT in loadfat)
#                      - added some constants
#                      - added header values checks
#                      - added some docstrings
#                      - getsect: bugfix in case sectors >512 bytes
#                      - getsect: added conformity checks
#                      - DEBUG_MODE constant to activate debug display
# 2007-09-04 v0.13 PL: - improved/translated (lots of) comments
#                      - updated license
#                      - converted tabs to 4 spaces

#-----------------------------------------------------------------------------
# TODO:
# - fix Unicode names handling
# - fix handling of DIFSECT blocks in FAT (not stop)
# - add stricter checks in decoding
# - add (optional) checks on FAT block chains integrity to detect crossed
#   sectors, loops, ...
# - in __main__ display the whole object tree (not only 1st level), and allow
#   to extract objects, or provide a sample script to do it.
# - see also original notes and FIXME below
#-----------------------------------------------------------------------------

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

#--- LICENSE ------------------------------------------------------------------

# OleFileIO_PL is an improved version of the OleFileIO module from the
# Python Imaging Library (PIL).

# OleFileIO_PL changes are Copyright (c) 2005-2007 by Philippe Lagadec
#
# The Python Imaging Library (PIL) is
#    Copyright (c) 1997-2005 by Secret Labs AB
#    Copyright (c) 1995-2005 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its associated
# documentation, you agree that you have read, understood, and will comply with
# the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and its
# associated documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies, and that both
# that copyright notice and this permission notice appear in supporting
# documentation, and that the name of Secret Labs AB or the author(s) not be used
# in advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.
#
# SECRET LABS AB AND THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
# IN NO EVENT SHALL SECRET LABS AB OR THE AUTHORS BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

#------------------------------------------------------------------------------

import string, StringIO, struct, array, os.path

#[PL] DEBUG display mode:
DEBUG_MODE = False

if DEBUG_MODE:
    def debug(msg):
        print msg
else:
    def debug(msg):
        pass

def i16(c, o = 0):
    return ord(c[o])+(ord(c[o+1])<<8)

def i32(c, o = 0):
    return int(ord(c[o])+(ord(c[o+1])<<8)+(ord(c[o+2])<<16)+(ord(c[o+3])<<24))
    # [PL]: added int() because "<<" gives long int since Python 2.4


MAGIC = '\320\317\021\340\241\261\032\341'

# [PL]: added constants (from AAF specifications)
MAXREGSECT = 0xFFFFFFFAL; # maximum SECT
DIFSECT    = 0xFFFFFFFCL; # denotes a DIFAT sector in a FAT
FATSECT    = 0xFFFFFFFDL; # denotes a FAT sector in a FAT
ENDOFCHAIN = 0xFFFFFFFEL; # end of a virtual stream chain
FREESECT   = 0xFFFFFFFFL; # unallocated sector
MAXREGSID  = 0xFFFFFFFAL; # maximum directory entry ID
NOSTREAM   = 0xFFFFFFFFL; # unallocated directory entry

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

        # [PL]       while sect != -2: # 0xFFFFFFFEL:
        while sect != ENDOFCHAIN:
            fp.seek(offset + sectorsize * sect)
            data.append(fp.read(sectorsize))
            # [PL] if pointer is out of the FAT an exception is raised
            if sect >= len(fat) :
                raise IOError, 'incorrect FAT'
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

        # [PL] conformity check
        if sid >= len(sidlist) :
            raise IOError, 'incorrect SID'

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

        # [PL]: original code from PIL 1.1.5
        #if sid != -1
        # [PL]: necessary fix for Python 2.4
        #if sid != -1 and sid != 0xFFFFFFFFL:
        # [PL]: new fix 22/02/2006
        if sid != NOSTREAM:

            # the directory entries are organized as a red-black tree.
            # the following piece of code does an ordered traversal of
            # such a tree (at least that's what I hope ;-)

            stack = [self.sid]

            # start at leftmost position

            left, right, child = sidlist[sid][4]

            #[PL] while left != -1 and left != 0xFFFFFFFFL:
            if left != NOSTREAM:
                stack.append(sid)
                sid = left
                left, right, child = sidlist[sid][4]

            while sid != self.sid:

                self.kids.append(_OleDirectoryEntry(sidlist, sid))

                # try to move right

                # [PL] conformity check
                if sid >= len(sidlist) :
                    raise IOError, 'incorrect SID'

                left, right, child = sidlist[sid][4]
                #[PL] if right != -1 and right != 0xFFFFFFFFL:
                if right != NOSTREAM:
                    # and then back to the left
                    sid = right
                    while 1:

                        # [PL] conformity check
                        if sid >= len(sidlist) :
                            raise IOError, 'incorrect SID'

                        left, right, child = sidlist[sid][4]
                        #[PL] if left == -1 or left == 0xFFFFFFFFL:
                        if left == NOSTREAM:
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

        # [PL] header structure according to AAF specifications:
        ##Header
        ##struct StructuredStorageHeader { // [offset from start (bytes), length (bytes)]
        ##BYTE _abSig[8]; // [00H,08] {0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1,
        ##                // 0x1a, 0xe1} for current version
        ##CLSID _clsid;   // [08H,16] reserved must be zero (WriteClassStg/
        ##                // GetClassFile uses root directory class id)
        ##USHORT _uMinorVersion; // [18H,02] minor version of the format: 33 is
        ##                       // written by reference implementation
        ##USHORT _uDllVersion;   // [1AH,02] major version of the dll/format: 3 for
        ##                       // 512-byte sectors, 4 for 4 KB sectors
        ##USHORT _uByteOrder;    // [1CH,02] 0xFFFE: indicates Intel byte-ordering
        ##USHORT _uSectorShift;  // [1EH,02] size of sectors in power-of-two;
        ##                       // typically 9 indicating 512-byte sectors
        ##USHORT _uMiniSectorShift; // [20H,02] size of mini-sectors in power-of-two;
        ##                          // typically 6 indicating 64-byte mini-sectors
        ##USHORT _usReserved; // [22H,02] reserved, must be zero
        ##ULONG _ulReserved1; // [24H,04] reserved, must be zero
        ##FSINDEX _csectDir; // [28H,04] must be zero for 512-byte sectors,
        ##                   // number of SECTs in directory chain for 4 KB
        ##                   // sectors
        ##FSINDEX _csectFat; // [2CH,04] number of SECTs in the FAT chain
        ##SECT _sectDirStart; // [30H,04] first SECT in the directory chain
        ##DFSIGNATURE _signature; // [34H,04] signature used for transactions; must
        ##                        // be zero. The reference implementation
        ##                        // does not support transactions
        ##ULONG _ulMiniSectorCutoff; // [38H,04] maximum size for a mini stream;
        ##                           // typically 4096 bytes
        ##SECT _sectMiniFatStart; // [3CH,04] first SECT in the MiniFAT chain
        ##FSINDEX _csectMiniFat; // [40H,04] number of SECTs in the MiniFAT chain
        ##SECT _sectDifStart; // [44H,04] first SECT in the DIFAT chain
        ##FSINDEX _csectDif; // [48H,04] number of SECTs in the DIFAT chain
        ##SECT _sectFat[109]; // [4CH,436] the SECTs of first 109 FAT sectors
        ##};

        # [PL] header decoding:
        # '<' indicates little-endian byte ordering for Intel (cf. struct module help)
        fmt_header = '<8s16sHHHHHHLLLLLLLLLL'
        header_size = struct.calcsize(fmt_header)
        debug( "fmt_header size = %d, +FAT = %d" % (header_size, header_size + 109*4) )
        header1 = header[:header_size]
        (Sig, clsid, MinorVersion, DllVersion, ByteOrder, SectorShift,
        MiniSectorShift, Reserved, Reserved1, csectDir, self.csectFat, sectDirStart,
        signature, MiniSectorCutoff, MiniFatStart, csectMiniFat, self.sectDifStart,
        self.csectDif) = struct.unpack(fmt_header, header1)
        debug( struct.unpack(fmt_header,    header1))

        if Sig != '\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
            raise IOError, "incorrect OLE signature"
        if clsid != '\x00'*16:
            raise IOError, "incorrect CLSID in OLE header"
        debug( "MinorVersion = %d" % MinorVersion )
        debug( "DllVersion   = %d" % DllVersion )
        if DllVersion not in [3, 4]:
            raise IOError, "incorrect DllVersion in OLE header"
        debug( "ByteOrder    = %X" % ByteOrder )
        if ByteOrder != 0xFFFE:
            raise IOError, "incorrect ByteOrder in OLE header"
        SectorSize = 2**SectorShift
        debug( "SectorSize   = %d" % SectorSize )
        if SectorSize not in [512, 4096]:
            raise IOError, "incorrect SectorSize in OLE header"
        MiniSectorSize = 2**MiniSectorShift
        debug( "MiniSectorSize   = %d" % MiniSectorSize )
        if MiniSectorSize not in [64]:
            raise IOError, "incorrect MiniSectorSize in OLE header"
        if Reserved != 0 or Reserved1 != 0:
            raise IOError, "incorrect OLE header"
        debug( "csectDir     = %d" % csectDir )
        if SectorSize==512 and csectDir!=0:
            raise IOError, "incorrect csectDir in OLE header"
        debug( "csectFat     = %d" % self.csectFat )
        debug( "sectDirStart = %X" % sectDirStart )
        debug( "signature    = %d" % signature )
        if signature != 0:
            raise IOError, "incorrect OLE header"
        debug( "MiniSectorCutoff    = %d" % MiniSectorCutoff )
        debug( "MiniFatStart    = %X" % MiniFatStart )
        debug( "csectMiniFat    = %d" % csectMiniFat )
        debug( "sectDifStart    = %X" % self.sectDifStart )
        debug( "csectDif        = %d" % self.csectDif )

        # calculate the number of sectors in the file
        # (-1 because header doesn't count)
        self.nb_sect = (os.path.getsize(filename) / SectorSize) - 1
        debug( "Number of sectors in the file: %d" % self.nb_sect )

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

    def dumpfat(self, fat, firstindex=0):
        "Displays a part of FAT in human-readable form for debugging purpose"
        # [PL] added only for debug
        if not DEBUG_MODE:
            return
        # dictionary to convert special FAT values in human-readable strings
        VPL=8 # valeurs par ligne (8+1 * 8+1 = 81)
        fatnames = {
            FREESECT:   "..free..",
            ENDOFCHAIN: "[ END. ]",
            FATSECT:    "FATSECT ",
            DIFSECT:    "DIFSECT "
            }
        nbsect = len(fat)
        nlines = (nbsect+VPL-1)/VPL
        print "index",
        for i in range(VPL):
            print ("%8X" % i),
        print ""
        for l in range(nlines):
            index = l*VPL
            print ("%8X:" % (firstindex+index)),
            for i in range(index, index+VPL):
                if i>=nbsect:
                    break
                sect = fat[i]
                if sect in fatnames:
                    nom = fatnames[sect]
                else:
                    if sect == i+1:
                        nom = "    --->"
                    else:
                        nom = "%8X" % sect
                print nom,
            print ""

    def dumpsect(self, sector, firstindex=0):
        "Displays a sector in a human-readable form, for debugging purpose."
        if not DEBUG_MODE:
            return
        VPL=8 # number of values per line (8+1 * 8+1 = 81)
        tab = array.array('L', sector)
        nbsect = len(tab)
        nlines = (nbsect+VPL-1)/VPL
        print "index",
        for i in range(VPL):
            print ("%8X" % i),
        print ""
        for l in range(nlines):
            index = l*VPL
            print ("%8X:" % (firstindex+index)),
            for i in range(index, index+VPL):
                if i>=nbsect:
                    break
                sect = tab[i]
                nom = "%8X" % sect
                print nom,
            print ""



    def loadfat_sect(self, sect):
        "Adds the indexes of the given sector to the FAT"
        # un secteur de FAT est un tableau d'ulong
        if isinstance(sect, array.array):
            fat1 = sect
        else:
            fat1 = array.array('L', sect)
            self.dumpsect(sect)
        # la FAT est une chaîne de secteurs débutant au 1er index d'elle-même
        for isect in fat1:
            #print "isect = %X" % isect
            if isect == ENDOFCHAIN or isect == FREESECT:
                break
            s = self.getsect(isect)
            self.fat = self.fat + array.array('L', s)
        return isect


    def loadfat(self, header):
        """
        Load the FAT table.
        """
        # The header contains a sector  numbers
        # for the first 109 FAT sectors.  Additional sectors are
        # described by DIF blocks 

        sect = header[76:512]
        debug( "len(sect)=%d, so %d integers" % (len(sect), len(sect)/4) )
        #fat    = []
        # [PL] FAT is an array of 32 bits unsigned ints, it's more effective
        # to use an array than a list in Python.
        # It's initialized as empty first:
        self.fat = array.array('L')
        self.loadfat_sect(sect)
        #self.dumpfat(self.fat)
##      for i in range(0, len(sect), 4):
##          ix = i32(sect, i)
##          #[PL] if ix == -2 or ix == -1: # ix == 0xFFFFFFFEL or ix == 0xFFFFFFFFL:
##          if ix == 0xFFFFFFFEL or ix == 0xFFFFFFFFL:
##              break
##          s = self.getsect(ix)
##          #fat    = fat + map(lambda i, s=s: i32(s, i), range(0, len(s), 4))
##          fat = fat + array.array('L', s)
        if self.csectDif != 0:
            # [PL] There's a DIFAT because file is larger than 6.8MB
            # some checks just in case:
            if self.csectFat <= 109:
                # there must be at least 109 blocks in header and the rest in
                # DIFAT, so number of sectors must be >109.
                raise IOError, 'incorrect DIFAT, not enough sectors'
            if self.sectDifStart >= self.nb_sect:
                # initial DIFAT block index must be valid
                raise IOError, 'incorrect DIFAT, first index out of range'
            debug( "DIFAT analysis..." )
            # We compute the necessary number of DIFAT sectors :
            # (each DIFAT sector = 127 pointers + 1 towards next DIFAT sector)
            nb_difat = (self.csectFat-109 + 126)/127
            debug( "nb_difat = %d" % nb_difat )
            if self.csectDif != nb_difat:
                raise IOError, 'incorrect DIFAT'
            isect_difat = self.sectDifStart
            for i in xrange(nb_difat):
                debug( "DIFAT block %d, sector %X" % (i, isect_difat) )
                sector_difat = self.getsect(isect_difat)
                difat = array.array('L', sector_difat)
                self.dumpsect(sector_difat)
                self.loadfat_sect(difat[:127])
                # last DIFAT pointer is next DIFAT sector:
                isect_difat = difat[127]
                debug( "next DIFAT sector: %X" % isect_difat )
            # checks:
            if isect_difat not in [ENDOFCHAIN, FREESECT]:
                # last DIFAT pointer value must be ENDOFCHAIN or FREESECT
                raise IOError, 'incorrect end of DIFAT'
##          if len(self.fat) != self.csectFat:
##              # FAT should contain csectFat blocks
##              print "FAT length: %d instead of %d" % (len(self.fat), self.csectFat)
##              raise IOError, 'incorrect DIFAT'
        self.dumpfat(self.fat)

    def loadminifat(self):
        "Load the MINIFAT table."
        # This is stored in a standard  sub-
        # stream, pointed to by a header field.
        s = self._open(self.minifatsect).read()
        self.minifat = map(lambda i, s=s: i32(s, i), range(0, len(s), 4))

    def getsect(self, sect):
        "Read given sector"
        # [PL] this original code was wrong when sectors are 4KB instead of
        # 512 bytes:
        #self.fp.seek(512 + self.sectorsize * sect)
        #[PL]: added safety checks:
        #print "getsect(%X)" % sect
        try:
            self.fp.seek(self.sectorsize * (sect+1))
        except:
            raise IOError, 'wrong index for OLE sector'
        sector = self.fp.read(self.sectorsize)
        if len(sector) != self.sectorsize:
            raise IOError, 'incomplete OLE sector'
        return sector

    def _unicode(self, s):
        # Map unicode string to Latin 1

        # FIXME: some day, Python will provide an official way to handle
        # Unicode strings, but until then, this will have to do...
        return filter(ord, s)

    def loaddirectory(self, sect):
        """
        Load the directory.
        """
        # The directory is  stored in a standard
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

    # [PL] display quick usage info if launched from command-line
    if len(sys.argv) <= 1:
        print __doc__
        print "Launched from command line, this script parses OLE files and prints info."
        print ""
        sys.exit("usage: OleFileIO_PL.py <file> [file2 ...]")

    for file in sys.argv[1:]:
##      try:
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
##      except IOError, v:
##          print "***", "cannot read", file, "-", v
