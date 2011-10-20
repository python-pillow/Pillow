#!/usr/local/bin/python
# -*- coding: latin-1 -*-
"""
OleFileIO_PL:
    Module to read Microsoft OLE2 files (Structured Storage), such as
    Microsoft Office documents, Image Composer and FlashPix files,
    Outlook messages, ...

version 0.15 2007-11-25 Philippe Lagadec - http://lagasoft.free.fr

Project website: http://lagasoft.free.fr/python/olefileio

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
__date__    = "2007-11-25"
__version__ = '0.15'

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
# 2007-11-19 v0.14 PL: - added OleFileIO.raise_defect() to adapt sensitivity
#                      - improved _unicode() to use Python 2.x unicode support
#                      - fixed bug in _OleDirectoryEntry
# 2007-11-25 v0.15 PL: - added safety checks to detect malformed documents
#                      - fixed _OleStream which didn't check stream size
#                      - added/improved many docstrings and comments
#                      - moved helper functions _unicode and _clsid out of
#                        OleFileIO class
#                      - improved OleFileIO._find() to add Unix path syntax
#                      - OleFileIO._find() is now case-insensitive
#                      - added get_type() and get_rootentry_name()
#                      - rewritten loaddirectory and _OleDirectoryEntry

#-----------------------------------------------------------------------------
# TODO:
# - add underscore to each private method/constant, to avoid their display in
#   pydoc/epydoc documentation
# - replace all raised exceptions with raise_defect (at least in OleFileIO)
# - add dictionary of directory entries indexed on filenames to avoid using
#   _find() each time ?
# - fix Unicode names handling (find some way to stay compatible with Py1.5.2)
#   => if possible avoid converting names to Latin-1
# - fix handling of DIFSECT blocks in FAT (not stop)
# - add stricter checks in decoding
# - add (optional) checks on FAT block chains integrity to detect crossed
#   sectors, loops, ...
# - improve docstrings to show more sample uses
# - fix docstrings to follow epydoc format
# - see also original notes and FIXME below
# - remove all obsolete FIXMEs
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

MAGIC = '\320\317\021\340\241\261\032\341'

#[PL]: added constants for Sector IDs (from AAF specifications)
MAXREGSECT = 0xFFFFFFFAL; # maximum SECT
DIFSECT    = 0xFFFFFFFCL; # (-4) denotes a DIFAT sector in a FAT
FATSECT    = 0xFFFFFFFDL; # (-3) denotes a FAT sector in a FAT
ENDOFCHAIN = 0xFFFFFFFEL; # (-2) end of a virtual stream chain
FREESECT   = 0xFFFFFFFFL; # (-1) unallocated sector

#[PL]: added constants for Directory Entry IDs (from AAF specifications)
MAXREGSID  = 0xFFFFFFFAL; # maximum directory entry ID
NOSTREAM   = 0xFFFFFFFFL; # (-1) unallocated directory entry

#[PL] object types in storage (from AAF specifications)
STGTY_EMPTY     = 0 # empty directory entry (according to OpenOffice.org doc)
STGTY_STORAGE   = 1 # element is a storage object
STGTY_STREAM    = 2 # element is a stream object
STGTY_LOCKBYTES = 3 # element is an ILockBytes object
STGTY_PROPERTY  = 4 # element is an IPropertyStorage object
STGTY_ROOT      = 5 # element is a root storage


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

#[PL]: Defect levels to classify parsing errors - see OleFileIO.raise_defect()
DEFECT_UNSURE =    10    # a case which looks weird, but not sure it's a defect
DEFECT_POTENTIAL = 20    # a potential defect
DEFECT_INCORRECT = 30    # an error according to specifications, but parsing
                         # can go on
DEFECT_FATAL =     40    # an error which cannot be ignored, parsing is
                         # impossible

#--- FUNCTIONS ----------------------------------------------------------------

#TODO: replace i16 and i32 with more readable struct.unpack equivalent
def i16(c, o = 0):
    """
    Converts a 2-bytes (16 bits) string to an integer.

    c: string containing bytes to convert
    o: offset of bytes to convert in string
    """
    return ord(c[o])+(ord(c[o+1])<<8)


def i32(c, o = 0):
    """
    Converts a 4-bytes (32 bits) string to an integer.

    c: string containing bytes to convert
    o: offset of bytes to convert in string
    """
    return int(ord(c[o])+(ord(c[o+1])<<8)+(ord(c[o+2])<<16)+(ord(c[o+3])<<24))
    # [PL]: added int() because "<<" gives long int since Python 2.4


def _clsid(clsid):
    """
    Converts a CLSID to a human-readable string.
    clsid: string of length 16.
    """
    assert len(clsid) == 16
    if clsid == "\0" * len(clsid):
        return ""
    return (("%08X-%04X-%04X-%02X%02X-" + "%02X" * 6) %
            ((i32(clsid, 0), i16(clsid, 4), i16(clsid, 6)) +
            tuple(map(ord, clsid[8:16]))))


def _unicode(s):
    """
    Map unicode string to Latin 1.
    """
    #[PL]: use Python Unicode features when available (Python>=2.0):
    #TODO: test this with old Python versions <2.0
    #TODO: test if it OleFileIO works with Unicode strings, instead of
    #      converting to Latin-1.
    try:
        # First the string is converted to plain Unicode:
        # (assuming it is encoded as UTF-16 little-endian)
        u = unicode(s, 'UTF-16LE')
    except NameError:
        # If the unicode function does not exist, we assume this is an old
        # Python version without Unicode support.
        # Null bytes are simply removed (this only works with usual Latin-1
        # strings which do not contain unicode characters>256):
        return filter(ord, s)
    except ValueError:
        # there was an error during UTF-16 to Unicode decoding:
        self.raise_defect(DEFECT_INCORRECT, 'incorrect Unicode name')
        # if no exception raised, fallback to foolproof version:
        return filter(ord, s)
    try:
        # Second the unicode string is converted to Latin-1
        return u.encode('latin_1')
    except UnicodeError: # possible issue: this exception didn't exist before
        # there was an error during Unicode to Latin-1 encoding:
        self.raise_defect(DEFECT_INCORRECT, 'incorrect Unicode name')
        # if no exception raised, fallback to foolproof version:
        return filter(ord, s)


#=== CLASSES ==================================================================

#--- _OleStream ---------------------------------------------------------------

class _OleStream(StringIO.StringIO):
    """
    OLE2 Stream

    Returns a read-only file object which can be used to read
    the contents of a OLE stream (instance of the StringIO class).
    To open a stream, use the openstream method in the OleFile class.

    This function can be used with either ordinary streams,
    or ministreams, depending on the offset, sectorsize, and
    fat table arguments.

    Attributes:
        - size: actual size of data stream, after it was opened.
    """

    # FIXME: should store the list of sects obtained by following
    # the fat chain, and load new sectors on demand instead of
    # loading it all in one go.

    def __init__(self, fp, sect, size, offset, sectorsize, fat):
        """
        Constructor for _OleStream class.

        fp        : file object, the OLE container
        sect      : sector index of first sector in the stream
        size      : total size of the stream
        offset    : offset in bytes for the first FAT or MiniFAT sector
        sectorsize: size of one sector
        fat       : array/list of sector indexes (FAT or MiniFAT)
        return    : a StringIO instance containing the OLE stream
        """
        debug('_OleStream.__init__:')
        debug('  size=%d, offset=%d, sectorsize=%d, len(fat)=%d'
            %(size,offset,sectorsize,len(fat)))
        #[PL] To detect malformed documents with FAT loops, we compute the
        # expected number of sectors in the stream:
        if size==0x7FFFFFFF:
            # this is the case when called from OleFileIO._open(), and stream
            # size is not known in advance (for example when reading the
            # Directory stream). Then we can only guess maximum size:
            size = len(fat)*sectorsize
        nb_sectors = (size + (sectorsize-1)) / sectorsize
        # This number should (at least) be less than the total number of
        # sectors in the given FAT:
        if nb_sectors > len(fat):
            raise IOError, 'malformed OLE document, stream too large'
        # optimization(?): data is first a list of strings, and join() is called
        # at the end to concatenate all in one string.
        # (this may not be really useful with recent Python versions)
        data = []
        #[PL] first sector index should be within FAT or ENDOFCHAIN:
        if sect != ENDOFCHAIN and (sect<0 or sect>=len(fat)):
            raise IOError, 'incorrect OLE FAT, sector index out of range'
        #[PL] A fixed-length for loop is used instead of an undefined while
        # loop to avoid DoS attacks:
        for i in xrange(nb_sectors):
            #TODO: check if this works with 4K sectors:
            fp.seek(offset + sectorsize * sect)
            sector_data = fp.read(sectorsize)
            # [PL] check if there was enough data:
            if len(sector_data) != sectorsize:
                raise IOError, 'incomplete OLE sector'
            data.append(sector_data)
            # jump to next sector in the FAT:
            try:
                #[PL] sector index should not be negative, but Python allows it
                if sect<0: raise IndexError
                sect = fat[sect]
                if sect == ENDOFCHAIN:
                    # this may happen when size was not known:
                    break
            except IndexError:
                # [PL] if pointer is out of the FAT an exception is raised
                raise IOError, 'incorrect OLE FAT, sector index out of range'
        #[PL] Last sector should be a "end of chain" marker:
        if sect != ENDOFCHAIN:
            raise IOError, 'incorrect last sector index in OLE stream'
        data = string.join(data, "")
        # Data is truncated to the actual stream size:
        if len(data) > size:
            data = data[:size]
            # actual stream size is stored for future use:
            self.size = size
        else:
            # actual stream size was not known, now we know the size of read
            # data:
            self.size = len(data)
        # when all data is read in memory, StringIO constructor is called
        StringIO.StringIO.__init__(self, data)
        # Then the _OleStream object can be used as a read-only file object.


#--- _OleDirectoryEntry -------------------------------------------------------

# FIXME: should add a counter in here to avoid looping forever
# if the tree is broken.

class _OleDirectoryEntry:

    """
    OLE2 Directory Entry
    """

    #[PL] parsing code moved from OleFileIO.loaddirectory

    # struct to parse directory entries:
    # <: little-endian byte order
    # 64s: string containing entry name in unicode (max 31 chars) + null char
    # H: uint16, number of bytes used in name buffer, including null = (len+1)*2
    # B: uint8, dir entry type (between 0 and 5)
    # B: uint8, color: 0=black, 1=red
    # I: uint32, index of left child node in the red-black tree, NOSTREAM if none
    # I: uint32, index of right child node in the red-black tree, NOSTREAM if none
    # I: uint32, index of child root node if it is a storage, else NOSTREAM
    # 16s: CLSID, unique identifier (only used if it is a storage)
    # I: uint32, user flags
    # 8s: uint64, creation timestamp or zero
    # 8s: uint64, modification timestamp or zero
    # I: uint32, SID of first sector if stream or ministream, SID of 1st sector
    #    of stream containing ministreams if root entry, 0 otherwise
    # I: uint32, total stream size in bytes if stream (low 32 bits), 0 otherwise
    # I: uint32, total stream size in bytes if stream (high 32 bits), 0 otherwise
    STRUCT_DIRENTRY = '<64sHBBIII16sI8s8sIII'
    # size of a directory entry: 128 bytes
    DIRENTRY_SIZE = 128
    assert struct.calcsize(STRUCT_DIRENTRY) == DIRENTRY_SIZE


    def __init__(self, entry, sid, olefile):
        """
        Constructor for an _OleDirectoryEntry object.
        Parses a 128-bytes entry from the OLE Directory stream.
        
        entry: string (must be 128 bytes long)
        olefile: OleFileIO containing this directory entry
        """
        self.sid = sid
        # ref to olefile is stored for future use
        self.olefile = olefile
        # kids is the list of children entries, if this entry is a storage:
        # (list of _OleDirectoryEntry objects)
        self.kids = []
        # flag used to detect if the entry is referenced more than once in
        # directory:
        self.used = False
        # decode DirEntry
        (
            name,
            namelength,
            self.entry_type,
            self.color,
            self.sid_left,
            self.sid_right,
            self.sid_child,
            clsid,
            self.dwUserFlags,
            self.createTime,
            self.modifyTime,
            self.isectStart,
            sizeLow,
            sizeHigh
        ) = struct.unpack(_OleDirectoryEntry.STRUCT_DIRENTRY, entry)
        if self.entry_type not in [STGTY_ROOT, STGTY_STORAGE, STGTY_STREAM, STGTY_EMPTY]:
            olefile.raise_defect(DEFECT_INCORRECT, 'unhandled OLE storage type')
        #debug (struct.unpack(fmt_entry, entry[:len_entry]))
        # name should be at most 31 unicode characters + null character,
        # so 64 bytes in total (31*2 + 2):
        if namelength>64:
            olefile.raise_defect(DEFECT_INCORRECT, 'incorrect DirEntry name length')
            # if exception not raised, namelength is set to the maximum value:
            namelength = 64
        # only characters without ending null char are kept:
        name = name[:(namelength-2)]
        # name is converted from unicode to Latin-1:
        self.name = _unicode(name)
        # sizeHigh is only used for 4K sectors, it should be zero for 512 bytes
        # sectors:
        if olefile.sectorsize == 512 and sizeHigh != 0:
            olefile.raise_defect(DEFECT_INCORRECT, 'incorrect OLE stream size')
        self.size = sizeLow + (long(sizeHigh)<<32)
        self.clsid = _clsid(clsid)

        debug('DirEntry SID=%d: %s' % (self.sid, self.name))
        debug(' - type: %d' % self.entry_type)
        debug(' - sect: %d' % self.isectStart)
        debug(' - size: %d (sizeLow=%d, sizeHigh=%d)' % (self.size, sizeLow, sizeHigh))
        debug(' - SID left: %d, right: %d, child: %d' % (self.sid_left,
            self.sid_right, self.sid_child))


    def build_storage_tree(self):
        """
        Read and build the red-black tree attached to this _OleDirectoryEntry
        object, if it is a storage.
        Note that this method builds a tree of all subentries, so it should
        only be called for the root object once.
        """
        debug('build_storage_tree: SID=%d - %s - sid_child=%d'
            % (self.sid, self.name, self.sid_child))
        if self.sid_child != NOSTREAM:
            # if child SID is not NOSTREAM, then this entry is a storage.
            # Let's walk through the tree of children to fill the kids list:
            self.append_kids(self.sid_child)

            # Note from OpenOffice documentation: the safest way is to
            # recreate the tree because some implementations may store broken
            # red-black trees...

            # in the OLE file, entries are sorted on (length, name).
            # for convenience, we sort them on name instead:
            # (see __cmp__ method in this class)
            self.kids.sort()


    def append_kids(self, child_sid):
        """
        Walk through red-black tree of children of this directory entry to add
        all of them to the kids list. (recursive method)

        child_sid : index of child directory entry to use, or None when called
                    first time for the root. (only used during recursion)
        """
        #[PL] this method was added to use simple recursion instead of a complex
        # algorithm.
        # if this is not a storage or a leaf of the tree, nothing to do:
        if child_sid == NOSTREAM:
            return
        # check if child SID is in the proper range:
        if child_sid<0 or child_sid>=len(self.olefile.direntries):
            self.olefile.raise_defect(DEFECT_FATAL, 'OLE DirEntry index out of range')
        # get child direntry:
        child = self.olefile.direntries[child_sid]
        debug('append_kids: child_sid=%d - %s - sid_left=%d, sid_right=%d, sid_child=%d'
            % (child.sid, child.name, child.sid_left, child.sid_right, child.sid_child))
        # the directory entries are organized as a red-black tree.
        # (cf. Wikipedia for details)
        # First walk through left side of the tree:
        self.append_kids(child.sid_left)
        # Then the child_sid _OleDirectoryEntry object is appended to the
        # kids list:
        self.kids.append(child)
        # Check if kid was not already referenced in a storage:
        if child.used:
            self.olefile.raise_defect(DEFECT_INCORRECT,
                'OLE Entry referenced more than once')
        child.used = True
        # Finally walk through right side of the tree:
        self.append_kids(child.sid_right)
        # Afterwards build kid's own tree if it's also a storage:
        child.build_storage_tree()


    def __cmp__(self, other):
        "Compare entries by name"
        return cmp(self.name, other.name)


    def dump(self, tab = 0):
        "Dump this entry, and all its subentries (for debug purposes only)"
        TYPES = ["(invalid)", "(storage)", "(stream)", "(lockbytes)",
                 "(property)", "(root)"]

        print " "*tab + repr(self.name), TYPES[self.entry_type],
        if self.entry_type in (STGTY_STREAM, STGTY_ROOT):
            print self.size, "bytes",
        print
        if self.entry_type in (STGTY_STORAGE, STGTY_ROOT) and self.clsid:
            print " "*tab + "{%s}" % self.clsid

        for kid in self.kids:
            kid.dump(tab + 2)


#--- OleFileIO ----------------------------------------------------------------

class OleFileIO:
    """
    OLE container object

    This class encapsulates the interface to an OLE 2 structured
    storage file.  Use the {@link listdir} and {@link openstream} methods to
    access the contents of this file.

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

    def __init__(self, filename = None, raise_defects=DEFECT_FATAL):
        """
        Constructor for OleFileIO class.
        
        filename: file to open.
        raise_defects: minimal level for defects to be raised as exceptions.
        (use DEFECT_FATAL for a typical application, DEFECT_INCORRECT for a
        security-oriented application, see source code for details)
        """
        self.raise_defects_level = raise_defects
        if filename:
            self.open(filename)


    def raise_defect(self, defect_level, message):
        """
        This method should be called for any defect found during file parsing.
        It may raise an IOError exception according to the minimal level chosen
        for the OleFileIO object.

        defect_level: defect level, possible values are:
            DEFECT_UNSURE    : a case which looks weird, but not sure it's a defect
            DEFECT_POTENTIAL : a potential defect
            DEFECT_INCORRECT : an error according to specifications, but parsing can go on
            DEFECT_FATAL     : an error which cannot be ignored, parsing is impossible
        message: string describing the defect, used with raised exception.
        """
        # added by [PL]
        if defect_level >= self.raise_defects_level:
            raise IOError, message
        

    def open(self, filename):
        """
        Open an OLE2 file.
        Reads the header, FAT and directory.
        """
        if type(filename) == type(""):
            self.fp = open(filename, "rb")
        else:
            self.fp = filename

        header = self.fp.read(512)

        if len(header) != 512 or header[:8] != MAGIC:
            self.raise_defect(DEFECT_FATAL, "not an OLE2 structured storage file")

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
            # OLE signature should always be present
            self.raise_defect(DEFECT_FATAL, "incorrect OLE signature")
        if clsid != '\x00'*16:
            # according to AAF specs, CLSID should always be zero
            self.raise_defect(DEFECT_INCORRECT, "incorrect CLSID in OLE header")
        debug( "MinorVersion = %d" % MinorVersion )
        debug( "DllVersion   = %d" % DllVersion )
        if DllVersion not in [3, 4]:
            # version 3: usual format, 512 bytes per sector
            # version 4: large format, 4K per sector
            self.raise_defect(DEFECT_INCORRECT, "incorrect DllVersion in OLE header")
        debug( "ByteOrder    = %X" % ByteOrder )
        if ByteOrder != 0xFFFE:
            # For now only common little-endian documents are handled correctly
            self.raise_defect(DEFECT_FATAL, "incorrect ByteOrder in OLE header")
            # TODO: add big-endian support for documents created on Mac ?
        SectorSize = 2**SectorShift
        debug( "SectorSize   = %d" % SectorSize )
        if SectorSize not in [512, 4096]:
            self.raise_defect(DEFECT_INCORRECT, "incorrect SectorSize in OLE header")
        if (DllVersion==3 and SectorSize!=512) or (DllVersion==4 and SectorSize!=4096):
            self.raise_defect(DEFECT_INCORRECT, "SectorSize does not match DllVersion in OLE header")
        MiniSectorSize = 2**MiniSectorShift
        debug( "MiniSectorSize   = %d" % MiniSectorSize )
        if MiniSectorSize not in [64]:
            self.raise_defect(DEFECT_INCORRECT, "incorrect MiniSectorSize in OLE header")
        if Reserved != 0 or Reserved1 != 0:
            self.raise_defect(DEFECT_INCORRECT, "incorrect OLE header")
        debug( "csectDir     = %d" % csectDir )
        if SectorSize==512 and csectDir!=0:
            self.raise_defect(DEFECT_INCORRECT, "incorrect csectDir in OLE header")
        debug( "csectFat     = %d" % self.csectFat )
        debug( "sectDirStart = %X" % sectDirStart )
        debug( "signature    = %d" % signature )
        if signature != 0:
            self.raise_defect(DEFECT_INCORRECT, "incorrect OLE header")
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
        clsid = _clsid(header[8:24])

        self.sectorsize = 1 << i16(header, 30)
        self.minisectorsize = 1 << i16(header, 32)

        self.minisectorcutoff = i32(header, 56)

        # Load file allocation tables
        self.loadfat(header)

        # Load direcory.  This sets both the direntries list (ordered by sid)
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
        """
        Adds the indexes of the given sector to the FAT
        sect: string containing the first FAT sector, or array of long integers
        return: index of last FAT sector.
        """
        # a FAT sector is an array of ulong integers.
        if isinstance(sect, array.array):
            # if sect is already an array it is directly used
            fat1 = sect
        else:
            # if it's a raw sector, it is parsed in an array
            fat1 = array.array('L', sect)
            self.dumpsect(sect)
        # The FAT is a sector chain starting at the first index of itself.
        for isect in fat1:
            #print "isect = %X" % isect
            if isect == ENDOFCHAIN or isect == FREESECT:
                # the end of the sector chain has been reached
                break
            # read the FAT sector
            s = self.getsect(isect)
            # parse it as an array of 32 bits integers, and add it to the
            # global FAT array
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
                self.raise_defect(DEFECT_INCORRECT, 'incorrect DIFAT, not enough sectors')
            if self.sectDifStart >= self.nb_sect:
                # initial DIFAT block index must be valid
                self.raise_defect(DEFECT_FATAL, 'incorrect DIFAT, first index out of range')
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
                #TODO: check if corresponding FAT SID = DIFSECT
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
        """
        Load the MiniFAT table.
        """
        # This is stored in a standard  sub-stream, pointed to by a header
        # field.
        s = self._open(self.minifatsect).read()
        #[PL] Old code replaced by an array:
        #self.minifat = map(lambda i, s=s: i32(s, i), range(0, len(s), 4))
        self.minifat = array.array('L', s)


    def getsect(self, sect):
        """
        Read given sector from file on disk.
        sect: sector index
        returns a string containing the sector data.
        """
        # [PL] this original code was wrong when sectors are 4KB instead of
        # 512 bytes:
        #self.fp.seek(512 + self.sectorsize * sect)
        #[PL]: added safety checks:
        #print "getsect(%X)" % sect
        try:
            self.fp.seek(self.sectorsize * (sect+1))
        except:
            self.raise_defect(DEFECT_FATAL, 'wrong index for OLE sector')
        sector = self.fp.read(self.sectorsize)
        if len(sector) != self.sectorsize:
            self.raise_defect(DEFECT_FATAL, 'incomplete OLE sector')
        return sector


    def loaddirectory(self, sect):
        """
        Load the directory.
        sect: sector index of directory stream.
        """
        # The directory is  stored in a standard
        # substream, independent of its size.

        # open directory stream as a read-only file:
        # (stream size is not known in advance)
        fp = self._open(sect)

        #[PL] to detect malformed documents and avoid DoS attacks, the maximum
        # number of directory entries can be calculated:
        max_entries = fp.size / 128
        debug('loaddirectory: size=%d, max_entries=%d' % (fp.size, max_entries))

        # Create list of directory entries
        self.direntries = []
        for sid in xrange(max_entries):
            entry = fp.read(128)
            if not entry:
                break
            self.direntries.append(_OleDirectoryEntry(entry, sid, self))
        # Root entry is the first entry:
        self.root = self.direntries[0]
        # read and build all storage trees, starting from the root:
        self.root.build_storage_tree()


    def dumpdirectory(self):
        """
        Dump directory (for debugging only)
        """
        self.root.dump()


    def _open(self, start, size = 0x7FFFFFFF):
        """
        Open a stream, either in FAT or MiniFAT according to its size.
        (openstream helper)
        
        start: index of first sector
        size: size of stream (or nothing if size is unknown)
        """
        # stream size is compared to the MiniSectorCutoff threshold:
        if size < self.minisectorcutoff:
            # ministream object
            if not self.ministream:
                # load MiniFAT if it wasn't already done:
                self.loadminifat()
                # The first sector index of the miniFAT stream is stored in the
                # root directory entry:
                self.ministream = self._open(self.root.isectStart)
            return _OleStream(self.ministream, start, size, 0,
                              self.minisectorsize, self.minifat)
        else:
            # standard stream
            return _OleStream(self.fp, start, size, 512,
                              self.sectorsize, self.fat)


    def _list(self, files, prefix, node):
        """
        (listdir helper)
        files: list of files to fill in
        prefix: current location in storage tree (list of names)
        node: current node (_OleDirectoryEntry object)
        """
        prefix = prefix + [node.name]
        for entry in node.kids:
            if entry.kids:
                self._list(files, prefix, entry)
            else:
                files.append(prefix[1:] + [entry.name])


    def listdir(self):
        """
        Return a list of streams stored in this file
        """
        files = []
        self._list(files, [], self.root)
        return files


    def _find(self, filename):
        """
        Returns directory entry of given filename. (openstream helper)
        Note: this method is case-insensitive.

        filename: path of stream in storage tree (except root entry), either:
            - a string using Unix path syntax, for example:
              'storage_1/storage_1.2/stream'
            - a list of storage filenames, path to the desired stream/storage.
              Example: ['storage_1', 'storage_1.2', 'stream']
        return: sid of requested filename
        raise IOError if file not found
        """

        # if filename is a string instead of a list, split it on slashes to
        # convert to a list:
        if isinstance(filename, basestring):
            filename = filename.split('/')
        # walk across storage tree, following given path:
        node = self.root
        for name in filename:
            for kid in node.kids:
                if kid.name.lower() == name.lower():
                    break
            else:
                raise IOError, "file not found"
            node = kid
        return node.sid


    def openstream(self, filename):
        """
        Open a stream as a read-only file object (StringIO).
        
        filename: path of stream in storage tree (except root entry), either:
            - a string using Unix path syntax, for example:
              'storage_1/storage_1.2/stream'
            - a list of storage filenames, path to the desired stream/storage.
              Example: ['storage_1', 'storage_1.2', 'stream']
        return: file object (read-only)
        raise IOError if filename not found, or if this is not a stream.
        """
        sid = self._find(filename)
        entry = self.direntries[sid]
        if entry.entry_type != STGTY_STREAM:
            raise IOError, "this file is not a stream"
        return self._open(entry.isectStart, entry.size)


    def get_type(self, filename):
        """
        Test if given filename exists as a stream or a storage in the OLE
        container, and return its type.

        filename: path of stream in storage tree (except root entry), either:
            - a string using Unix path syntax, for example:
              'storage_1/storage_1.2/stream'
            - a list of storage filenames, path to the desired stream/storage.
              Example: ['storage_1', 'storage_1.2', 'stream']
        return: False if object does not exist, its entry type (>0) otherwise:
            - STGTY_STREAM: a stream
            - STGTY_STORAGE: a storage
            - STGTY_ROOT: the root entry
        """
        try:
            sid = self._find(filename)
            entry = self.direntries[sid]
            return entry.entry_type
        except:
            return False


    def get_rootentry_name(self):
        """
        Return root entry name. Should usually be 'Root Entry' or 'R' in most
        implementations.
        """
        return self.root.name


    def getproperties(self, filename):
        """
        Return properties described in substream

        filename: path of stream in storage tree (except root entry), either:
            - a string using Unix path syntax, for example:
              'storage_1/storage_1.2/stream'
            - a list of storage filenames, path to the desired stream/storage.
              Example: ['storage_1', 'storage_1.2', 'stream']
        """
        fp = self.openstream(filename)

        data = {}

        # header
        s = fp.read(28)
        clsid = _clsid(s[8:24])

        # format id
        s = fp.read(20)
        fmtid = _clsid(s[:16])
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
                value = _clsid(s[offset+4:offset+20])
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

    for filename in sys.argv[1:]:
##      try:
            ole = OleFileIO(filename, raise_defects=DEFECT_INCORRECT)
            print "-" * 68
            print filename
            print "-" * 68
            ole.dumpdirectory()
            for streamname in ole.listdir():
                if streamname[-1][0] == "\005":
                    print streamname, ": properties"
                    props = ole.getproperties(streamname)
                    props = props.items()
                    props.sort()
                    for k, v in props:
                        print "   ", k, v
            root = ole.get_rootentry_name()
            print 'Root entry name: "%s"' % root
            if ole.get_type('macros/vba'):
                print "This may be a Word document with VBA macros."
##      except IOError, v:
##          print "***", "cannot read", file, "-", v
