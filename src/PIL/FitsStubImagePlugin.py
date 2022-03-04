#
# The Python Imaging Library
# $Id$
#
# FITS stub adapter
#
# Copyright (c) 1998-2003 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import warnings

from . import FitsImagePlugin, Image, ImageFile

_handler = None


def register_handler(handler):
    """
    Install application-specific FITS image handler.

    :param handler: Handler object.
    """
    global _handler
    _handler = handler

    warnings.warn(
        "FitsStubImagePlugin is deprecated and will be removed in Pillow "
        "10 (2023-07-01). FITS images can now be read without a handler through "
        "FitsImagePlugin instead.",
        DeprecationWarning,
    )

    # Override FitsImagePlugin with this handler
    # for backwards compatibility
    try:
        Image.ID.remove(FITSStubImageFile.format)
    except ValueError:
        pass

    Image.register_open(
        FITSStubImageFile.format, FITSStubImageFile, FitsImagePlugin._accept
    )


class FITSStubImageFile(ImageFile.StubImageFile):

    format = FitsImagePlugin.FitsImageFile.format
    format_description = FitsImagePlugin.FitsImageFile.format_description

    def _open(self):
        offset = self.fp.tell()

        im = FitsImagePlugin.FitsImageFile(self.fp)
        self._size = im.size
        self.mode = im.mode
        self.tile = []

        self.fp.seek(offset)

        loader = self._load()
        if loader:
            loader.open(self)

    def _load(self):
        return _handler


def _save(im, fp, filename):
    raise OSError("FITS save handler not installed")


# --------------------------------------------------------------------
# Registry

Image.register_save(FITSStubImageFile.format, _save)
