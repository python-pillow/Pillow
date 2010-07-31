#
# The Python Imaging Library.
# $Id$
#
# base class for image file handlers
#
# history:
# 1995-09-09 fl   Created
# 1996-03-11 fl   Fixed load mechanism.
# 1996-04-15 fl   Added pcx/xbm decoders.
# 1996-04-30 fl   Added encoders.
# 1996-12-14 fl   Added load helpers
# 1997-01-11 fl   Use encode_to_file where possible
# 1997-08-27 fl   Flush output in _save
# 1998-03-05 fl   Use memory mapping for some modes
# 1999-02-04 fl   Use memory mapping also for "I;16" and "I;16B"
# 1999-05-31 fl   Added image parser
# 2000-10-12 fl   Set readonly flag on memory-mapped images
# 2002-03-20 fl   Use better messages for common decoder errors
# 2003-04-21 fl   Fall back on mmap/map_buffer if map is not available
# 2003-10-30 fl   Added StubImageFile class
# 2004-02-25 fl   Made incremental parser more robust
#
# Copyright (c) 1997-2004 by Secret Labs AB
# Copyright (c) 1995-2004 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import Image
import traceback, string, os

MAXBLOCK = 65536

SAFEBLOCK = 1024*1024

ERRORS = {
    -1: "image buffer overrun error",
    -2: "decoding error",
    -3: "unknown error",
    -8: "bad configuration",
    -9: "out of memory error"
}

def raise_ioerror(error):
    try:
        message = Image.core.getcodecstatus(error)
    except AttributeError:
        message = ERRORS.get(error)
    if not message:
        message = "decoder error %d" % error
    raise IOError(message + " when reading image file")

#
# --------------------------------------------------------------------
# Helpers

def _tilesort(t1, t2):
    # sort on offset
    return cmp(t1[2], t2[2])

#
# --------------------------------------------------------------------
# ImageFile base class

##
# Base class for image file handlers.

class ImageFile(Image.Image):
    "Base class for image file format handlers."

    def __init__(self, fp=None, filename=None):
        Image.Image.__init__(self)

        self.tile = None
        self.readonly = 1 # until we know better

        self.decoderconfig = ()
        self.decodermaxblock = MAXBLOCK

        if Image.isStringType(fp):
            # filename
            self.fp = open(fp, "rb")
            self.filename = fp
        else:
            # stream
            self.fp = fp
            self.filename = filename

        try:
            self._open()
        except IndexError, v: # end of data
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v
        except TypeError, v: # end of data (ord)
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v
        except KeyError, v: # unsupported mode
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v
        except EOFError, v: # got header but not the first frame
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v

        if not self.mode or self.size[0] <= 0:
            raise SyntaxError, "not identified by this driver"

    def draft(self, mode, size):
        "Set draft mode"

        pass

    def verify(self):
        "Check file integrity"

        # raise exception if something's wrong.  must be called
        # directly after open, and closes file when finished.
        self.fp = None

    def load(self):
        "Load image data based on tile list"

        pixel = Image.Image.load(self)

        if self.tile is None:
            raise IOError("cannot load this image")
        if not self.tile:
            return pixel

        self.map = None

        readonly = 0

        if self.filename and len(self.tile) == 1:
            # try memory mapping
            d, e, o, a = self.tile[0]
            if d == "raw" and a[0] == self.mode and a[0] in Image._MAPMODES:
                try:
                    if hasattr(Image.core, "map"):
                        # use built-in mapper
                        self.map = Image.core.map(self.filename)
                        self.map.seek(o)
                        self.im = self.map.readimage(
                            self.mode, self.size, a[1], a[2]
                            )
                    else:
                        # use mmap, if possible
                        import mmap
                        file = open(self.filename, "r+")
                        size = os.path.getsize(self.filename)
                        # FIXME: on Unix, use PROT_READ etc
                        self.map = mmap.mmap(file.fileno(), size)
                        self.im = Image.core.map_buffer(
                            self.map, self.size, d, e, o, a
                            )
                    readonly = 1
                except (AttributeError, EnvironmentError, ImportError):
                    self.map = None

        self.load_prepare()

        # look for read/seek overrides
        try:
            read = self.load_read
        except AttributeError:
            read = self.fp.read

        try:
            seek = self.load_seek
        except AttributeError:
            seek = self.fp.seek

        if not self.map:

            # sort tiles in file order
            self.tile.sort(_tilesort)

            try:
                # FIXME: This is a hack to handle TIFF's JpegTables tag.
                prefix = self.tile_prefix
            except AttributeError:
                prefix = ""

            for d, e, o, a in self.tile:
                d = Image._getdecoder(self.mode, d, a, self.decoderconfig)
                seek(o)
                try:
                    d.setimage(self.im, e)
                except ValueError:
                    continue
                b = prefix
                t = len(b)
                while 1:
                    s = read(self.decodermaxblock)
                    if not s:
                        self.tile = []
                        raise IOError("image file is truncated (%d bytes not processed)" % len(b))
                    b = b + s
                    n, e = d.decode(b)
                    if n < 0:
                        break
                    b = b[n:]
                    t = t + n

        self.tile = []
        self.readonly = readonly

        self.fp = None # might be shared

        if not self.map and e < 0:
            raise_ioerror(e)

        # post processing
        if hasattr(self, "tile_post_rotate"):
            # FIXME: This is a hack to handle rotated PCD's
            self.im = self.im.rotate(self.tile_post_rotate)
            self.size = self.im.size

        self.load_end()

        return Image.Image.load(self)

    def load_prepare(self):
        # create image memory if necessary
        if not self.im or\
           self.im.mode != self.mode or self.im.size != self.size:
            self.im = Image.core.new(self.mode, self.size)
        # create palette (optional)
        if self.mode == "P":
            Image.Image.load(self)

    def load_end(self):
        # may be overridden
        pass

    # may be defined for contained formats
    # def load_seek(self, pos):
    #     pass

    # may be defined for blocked formats (e.g. PNG)
    # def load_read(self, bytes):
    #     pass

##
# Base class for stub image loaders.
# <p>
# A stub loader is an image loader that can identify files of a
# certain format, but relies on external code to load the file.

class StubImageFile(ImageFile):
    "Base class for stub image loaders."

    def _open(self):
        raise NotImplementedError(
            "StubImageFile subclass must implement _open"
            )

    def load(self):
        loader = self._load()
        if loader is None:
            raise IOError("cannot find loader for this %s file" % self.format)
        image = loader.load(self)
        assert image is not None
        # become the other object (!)
        self.__class__ = image.__class__
        self.__dict__ = image.__dict__

    ##
    # (Hook) Find actual image loader.

    def _load(self):
        raise NotImplementedError(
            "StubImageFile subclass must implement _load"
            )

##
# (Internal) Support class for the <b>Parser</b> file.

class _ParserFile:
    # parser support class.

    def __init__(self, data):
        self.data = data
        self.offset = 0

    def close(self):
        self.data = self.offset = None

    def tell(self):
        return self.offset

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset = self.offset + offset
        else:
            # force error in Image.open
            raise IOError("illegal argument to seek")

    def read(self, bytes=0):
        pos = self.offset
        if bytes:
            data = self.data[pos:pos+bytes]
        else:
            data = self.data[pos:]
        self.offset = pos + len(data)
        return data

    def readline(self):
        # FIXME: this is slow!
        s = ""
        while 1:
            c = self.read(1)
            if not c:
                break
            s = s + c
            if c == "\n":
                break
        return s

##
# Incremental image parser.  This class implements the standard
# feed/close consumer interface.

class Parser:

    incremental = None
    image = None
    data = None
    decoder = None
    finished = 0

    ##
    # (Consumer) Reset the parser.  Note that you can only call this
    # method immediately after you've created a parser; parser
    # instances cannot be reused.

    def reset(self):
        assert self.data is None, "cannot reuse parsers"

    ##
    # (Consumer) Feed data to the parser.
    #
    # @param data A string buffer.
    # @exception IOError If the parser failed to parse the image file.

    def feed(self, data):
        # collect data

        if self.finished:
            return

        if self.data is None:
            self.data = data
        else:
            self.data = self.data + data

        # parse what we have
        if self.decoder:

            if self.offset > 0:
                # skip header
                skip = min(len(self.data), self.offset)
                self.data = self.data[skip:]
                self.offset = self.offset - skip
                if self.offset > 0 or not self.data:
                    return

            n, e = self.decoder.decode(self.data)

            if n < 0:
                # end of stream
                self.data = None
                self.finished = 1
                if e < 0:
                    # decoding error
                    self.image = None
                    raise_ioerror(e)
                else:
                    # end of image
                    return
            self.data = self.data[n:]

        elif self.image:

            # if we end up here with no decoder, this file cannot
            # be incrementally parsed.  wait until we've gotten all
            # available data
            pass

        else:

            # attempt to open this file
            try:
                try:
                    fp = _ParserFile(self.data)
                    im = Image.open(fp)
                finally:
                    fp.close() # explicitly close the virtual file
            except IOError:
                pass # not enough data
            else:
                flag = hasattr(im, "load_seek") or hasattr(im, "load_read")
                if flag or len(im.tile) != 1:
                    # custom load code, or multiple tiles
                    self.decode = None
                else:
                    # initialize decoder
                    im.load_prepare()
                    d, e, o, a = im.tile[0]
                    im.tile = []
                    self.decoder = Image._getdecoder(
                        im.mode, d, a, im.decoderconfig
                        )
                    self.decoder.setimage(im.im, e)

                    # calculate decoder offset
                    self.offset = o
                    if self.offset <= len(self.data):
                        self.data = self.data[self.offset:]
                        self.offset = 0

                self.image = im

    ##
    # (Consumer) Close the stream.
    #
    # @return An image object.
    # @exception IOError If the parser failed to parse the image file.

    def close(self):
        # finish decoding
        if self.decoder:
            # get rid of what's left in the buffers
            self.feed("")
            self.data = self.decoder = None
            if not self.finished:
                raise IOError("image was incomplete")
        if not self.image:
            raise IOError("cannot parse this image")
        if self.data:
            # incremental parsing not possible; reopen the file
            # not that we have all data
            try:
                fp = _ParserFile(self.data)
                self.image = Image.open(fp)
            finally:
                self.image.load()
                fp.close() # explicitly close the virtual file
        return self.image

# --------------------------------------------------------------------

##
# (Helper) Save image body to file.
#
# @param im Image object.
# @param fp File object.
# @param tile Tile list.

def _save(im, fp, tile):
    "Helper to save image based on tile list"

    im.load()
    if not hasattr(im, "encoderconfig"):
        im.encoderconfig = ()
    tile.sort(_tilesort)
    # FIXME: make MAXBLOCK a configuration parameter
    bufsize = max(MAXBLOCK, im.size[0] * 4) # see RawEncode.c
    try:
        fh = fp.fileno()
        fp.flush()
    except AttributeError:
        # compress to Python file-compatible object
        for e, b, o, a in tile:
            e = Image._getencoder(im.mode, e, a, im.encoderconfig)
            if o > 0:
                fp.seek(o, 0)
            e.setimage(im.im, b)
            while 1:
                l, s, d = e.encode(bufsize)
                fp.write(d)
                if s:
                    break
            if s < 0:
                raise IOError("encoder error %d when writing image file" % s)
    else:
        # slight speedup: compress to real file object
        for e, b, o, a in tile:
            e = Image._getencoder(im.mode, e, a, im.encoderconfig)
            if o > 0:
                fp.seek(o, 0)
            e.setimage(im.im, b)
            s = e.encode_to_file(fh, bufsize)
            if s < 0:
                raise IOError("encoder error %d when writing image file" % s)
    try:
        fp.flush()
    except: pass


##
# Reads large blocks in a safe way.  Unlike fp.read(n), this function
# doesn't trust the user.  If the requested size is larger than
# SAFEBLOCK, the file is read block by block.
#
# @param fp File handle.  Must implement a <b>read</b> method.
# @param size Number of bytes to read.
# @return A string containing up to <i>size</i> bytes of data.

def _safe_read(fp, size):
    if size <= 0:
        return ""
    if size <= SAFEBLOCK:
        return fp.read(size)
    data = []
    while size > 0:
        block = fp.read(min(size, SAFEBLOCK))
        if not block:
            break
        data.append(block)
        size = size - len(block)
    return string.join(data, "")
