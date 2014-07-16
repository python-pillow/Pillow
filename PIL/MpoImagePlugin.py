#
# The Python Imaging Library.
# $Id$
#
# MPO file handling
#
# See "Multi-Picture Format" (CIPA DC-007-Translation 2009, Standard of the
# Camera & Imaging Products Association)
#
# The multi-picture object combines multiple JPEG images (with a modified EXIF
# data format) into a single file. While it can theoretically be used much like
# a GIF animation, it is commonly used to represent 3D photographs and is (as
# of this writing) the most commonly used format by 3D cameras.
#
# History:
# 2014-03-13 Feneric   Created
#
# See the README file for information on usage and redistribution.
#

__version__ = "0.1"

from PIL import Image, JpegImagePlugin

def _accept(prefix):
    return JpegImagePlugin._accept(prefix)

def _save(im, fp, filename):
    return JpegImagePlugin._save(im, fp, filename)

##
# Image plugin for MPO images.

class MpoImageFile(JpegImagePlugin.JpegImageFile):

    format = "MPO"
    format_description = "MPO (CIPA DC-007)"

    def _open(self):
        JpegImagePlugin.JpegImageFile._open(self)
        self.__fp = self.fp # FIXME: hack
        self.__rewind = self.fp.tell()
        self.seek(0) # get ready to read first frame

    def seek(self, frame):

        if frame == 0:
            # rewind
            self.__offset = 0
            self.dispose = None
            self.__frame = -1
            self.__fp.seek(self.__rewind)

        if frame != self.__frame + 1:
            raise ValueError("cannot seek to frame %d" % frame)
        self.__frame = frame

    def tell(self):
        return self.__frame


# -------------------------------------------------------------------q-
# Registry stuff

Image.register_open("MPO", MpoImageFile, _accept)
Image.register_save("MPO", _save)

Image.register_extension("MPO", ".mpo")

Image.register_mime("MPO", "image/mpo")
