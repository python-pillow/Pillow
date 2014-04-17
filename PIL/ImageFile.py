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

from PIL import Image
from PIL._util import isPath
import traceback, os, sys
import io

MAXBLOCK = 65536

SAFEBLOCK = 1024*1024

LOAD_TRUNCATED_IMAGES = False

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

def _tilesort(t):
    # sort on offset
    return t[2]

#
# --------------------------------------------------------------------
# ImageFile base class

class ImageFile(Image.Image):
    "Base class for image file format handlers."

    def __init__(self, fp=None, filename=None):
        Image.Image.__init__(self)

        self.tile = None
        self.readonly = 1 # until we know better

        self.decoderconfig = ()
        self.decodermaxblock = MAXBLOCK

        if isPath(fp):
            # filename
            self.fp = open(fp, "rb")
            self.filename = fp
        else:
            # stream
            self.fp = fp
            self.filename = filename

        try:
            self._open()
        except IndexError as v: # end of data
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError(v)
        except TypeError as v: # end of data (ord)
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError(v)
        except KeyError as v: # unsupported mode
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError(v)
        except EOFError as v: # got header but not the first frame
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError(v)

        if not self.mode or self.size[0] <= 0:
            raise SyntaxError("not identified by this driver")

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

        if self.filename and len(self.tile) == 1 and not hasattr(sys, 'pypy_version_info'):
            # As of pypy 2.1.0, memory mapping was failing here.
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
            self.tile.sort(key=_tilesort)

            try:
                # FIXME: This is a hack to handle TIFF's JpegTables tag.
                prefix = self.tile_prefix
            except AttributeError:
                prefix = b""

            for d, e, o, a in self.tile:
                d = Image._getdecoder(self.mode, d, a, self.decoderconfig)
                seek(o)
                try:
                    d.setimage(self.im, e)
                except ValueError:
                    continue
                b = prefix
                t = len(b)
                while True:
                    try:
                        s = read(self.decodermaxblock)
                    except IndexError as ie: # truncated png/gif
                        if LOAD_TRUNCATED_IMAGES:
                            break
                        else:
                            raise IndexError(ie)

                    if not s and not d.handles_eof: # truncated jpeg
                        self.tile = []

                        # JpegDecode needs to clean things up here either way
                        # If we don't destroy the decompressor, we have a memory leak.
                        d.cleanup()

                        if LOAD_TRUNCATED_IMAGES:
                            break
                        else:
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

        if not self.map and (not LOAD_TRUNCATED_IMAGES or t == 0) and e < 0:
            # still raised if decoder fails to return anything
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


class StubImageFile(ImageFile):
    """
    Base class for stub image loaders.

    A stub loader is an image loader that can identify files of a
    certain format, but relies on external code to load the file.
    """

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

    def _load(self):
        "(Hook) Find actual image loader."
        raise NotImplementedError(
            "StubImageFile subclass must implement _load"
            )


class Parser:
    """
    Incremental image parser.  This class implements the standard
    feed/close consumer interface.

    In Python 2.x, this is an old-style class.
    """
    incremental = None
    image = None
    data = None
    decoder = None
    finished = 0

    def reset(self):
        """
        (Consumer) Reset the parser.  Note that you can only call this
        method immediately after you've created a parser; parser
        instances cannot be reused.
        """
        assert self.data is None, "cannot reuse parsers"

    def feed(self, data):
        """
        (Consumer) Feed data to the parser.

        :param data: A string buffer.
        :exception IOError: If the parser failed to parse the image file.
        """
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
                    fp = io.BytesIO(self.data)
                    im = Image.open(fp)
                finally:
                    fp.close() # explicitly close the virtual file
            except IOError:
                # traceback.print_exc()
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

    def close(self):
        """
        (Consumer) Close the stream.

        :returns: An image object.
        :exception IOError: If the parser failed to parse the image file either
                            because it cannot be identified or cannot be
                            decoded.
        """
        # finish decoding
        if self.decoder:
            # get rid of what's left in the buffers
            self.feed(b"")
            self.data = self.decoder = None
            if not self.finished:
                raise IOError("image was incomplete")
        if not self.image:
            raise IOError("cannot parse this image")
        if self.data:
            # incremental parsing not possible; reopen the file
            # not that we have all data
            try:
                fp = io.BytesIO(self.data)
                self.image = Image.open(fp)
            finally:
                self.image.load()
                fp.close() # explicitly close the virtual file
        return self.image

# --------------------------------------------------------------------

def _save(im, fp, tile, bufsize=0):
    """Helper to save image based on tile list

    :param im: Image object.
    :param fp: File object.
    :param tile: Tile list.
    :param bufsize: Optional buffer size
    """

    im.load()
    if not hasattr(im, "encoderconfig"):
        im.encoderconfig = ()
    tile.sort(key=_tilesort)
    # FIXME: make MAXBLOCK a configuration parameter
    # It would be great if we could have the encoder specifiy what it needs
    # But, it would need at least the image size in most cases. RawEncode is
    # a tricky case.
    bufsize = max(MAXBLOCK, bufsize, im.size[0] * 4) # see RawEncode.c
    try:
        fh = fp.fileno()
        fp.flush()
    except (AttributeError, io.UnsupportedOperation):
        # compress to Python file-compatible object
        for e, b, o, a in tile:
            e = Image._getencoder(im.mode, e, a, im.encoderconfig)
            if o > 0:
                fp.seek(o, 0)
            e.setimage(im.im, b)
            while True:
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


def _safe_read(fp, size):
    """
    Reads large blocks in a safe way.  Unlike fp.read(n), this function
    doesn't trust the user.  If the requested size is larger than
    SAFEBLOCK, the file is read block by block.

    :param fp: File handle.  Must implement a <b>read</b> method.
    :param size: Number of bytes to read.
    :returns: A string containing up to <i>size</i> bytes of data.
    """
    if size <= 0:
        return b""
    if size <= SAFEBLOCK:
        return fp.read(size)
    data = []
    while size > 0:
        block = fp.read(min(size, SAFEBLOCK))
        if not block:
            break
        data.append(block)
        size -= len(block)
    return b"".join(data)
