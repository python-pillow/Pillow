#
# The Python Imaging Library.
# $Id$
#
# Microsoft Image Composer support for PIL
#
# Notes:
#       uses TiffImagePlugin.py to read the actual image streams
#
# History:
#       97-01-20 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1997.
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.1"


from PIL import Image, TiffImagePlugin
from PIL.OleFileIO import *


#
# --------------------------------------------------------------------


def _accept(prefix):
    return prefix[:8] == MAGIC

##
# Image plugin for Microsoft's Image Composer file format.

class MicImageFile(TiffImagePlugin.TiffImageFile):

    format = "MIC"
    format_description = "Microsoft Image Composer"

    def _open(self):

        # read the OLE directory and see if this is a likely
        # to be a Microsoft Image Composer file

        try:
            self.ole = OleFileIO(self.fp)
        except IOError:
            raise SyntaxError("not an MIC file; invalid OLE file")

        # find ACI subfiles with Image members (maybe not the
        # best way to identify MIC files, but what the... ;-)

        self.images = []
        for file in self.ole.listdir():
            if file[1:] and file[0][-4:] == ".ACI" and file[1] == "Image":
                self.images.append(file)

        # if we didn't find any images, this is probably not
        # an MIC file.
        if not self.images:
            raise SyntaxError("not an MIC file; no image entries")

        self.__fp = self.fp
        self.frame = 0

        if len(self.images) > 1:
            self.category = Image.CONTAINER

        self.seek(0)

    def seek(self, frame):

        try:
            filename = self.images[frame]
        except IndexError:
            raise EOFError("no such frame")

        self.fp = self.ole.openstream(filename)

        TiffImagePlugin.TiffImageFile._open(self)

        self.frame = frame

    def tell(self):

        return self.frame

#
# --------------------------------------------------------------------

Image.register_open("MIC", MicImageFile, _accept)

Image.register_extension("MIC", ".mic")
