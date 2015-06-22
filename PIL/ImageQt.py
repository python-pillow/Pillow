#
# The Python Imaging Library.
# $Id$
#
# a simple Qt image interface.
#
# history:
# 2006-06-03 fl: created
# 2006-06-04 fl: inherit from QImage instead of wrapping it
# 2006-06-05 fl: removed toimage helper; move string support to ImageQt
# 2013-11-13 fl: add support for Qt5 (aurelien.ballier@cyclonit.com)
#
# Copyright (c) 2006 by Secret Labs AB
# Copyright (c) 2006 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import PIL
from PIL._util import isPath
from io import BytesIO

qt_is_installed = True
qt_version = None
try:
    from PyQt5.QtGui import QImage, qRgba, QPixmap
    from PyQt5.QtCore import QBuffer, QIODevice
    qt_version = '5'
except ImportError:
    try:
        from PyQt4.QtGui import QImage, qRgba, QPixmap
        from PyQt4.QtCore import QBuffer, QIODevice
        qt_version = '4'
    except ImportError:
        try:
            from PySide.QtGui import QImage, qRgba, QPixmap
            from PySide.QtCore import QBuffer, QIODevice
            qt_version = 'side'
        except ImportError:
            qt_is_installed = False


def rgb(r, g, b, a=255):
    """(Internal) Turns an RGB color into a Qt compatible color integer."""
    # use qRgb to pack the colors, and then turn the resulting long
    # into a negative integer with the same bitpattern.
    return (qRgba(r, g, b, a) & 0xffffffff)


# :param im A PIL Image object, or a file name
# (given either as Python string or a PyQt string object)

def fromqimage(im):
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    im.save(buffer, 'ppm')

    b = BytesIO()
    try:
        b.write(buffer.data())
    except TypeError:
        # workaround for Python 2
        b.write(str(buffer.data()))
    buffer.close()
    b.seek(0)

    return PIL.Image.open(b)


def fromqpixmap(im):
    return fromqimage(im)
    # buffer = QBuffer()
    # buffer.open(QIODevice.ReadWrite)
    # # im.save(buffer)
    # # What if png doesn't support some image features like animation?
    # im.save(buffer, 'ppm')
    # bytes_io = BytesIO()
    # bytes_io.write(buffer.data())
    # buffer.close()
    # bytes_io.seek(0)
    # return PIL.Image.open(bytes_io)


def _toqclass_helper(im):
    data = None
    colortable = None

    # handle filename, if given instead of image name
    if hasattr(im, "toUtf8"):
        # FIXME - is this really the best way to do this?
        if str is bytes:
            im = unicode(im.toUtf8(), "utf-8")
        else:
            im = str(im.toUtf8(), "utf-8")
    if isPath(im):
        im = PIL.Image.open(im)

    if im.mode == "1":
        format = QImage.Format_Mono
    elif im.mode == "L":
        format = QImage.Format_Indexed8
        colortable = []
        for i in range(256):
            colortable.append(rgb(i, i, i))
    elif im.mode == "P":
        format = QImage.Format_Indexed8
        colortable = []
        palette = im.getpalette()
        for i in range(0, len(palette), 3):
            colortable.append(rgb(*palette[i:i+3]))
    elif im.mode == "RGB":
        data = im.tobytes("raw", "BGRX")
        format = QImage.Format_RGB32
    elif im.mode == "RGBA":
        try:
            data = im.tobytes("raw", "BGRA")
        except SystemError:
            # workaround for earlier versions
            r, g, b, a = im.split()
            im = PIL.Image.merge("RGBA", (b, g, r, a))
        format = QImage.Format_ARGB32
    else:
        raise ValueError("unsupported image mode %r" % im.mode)

    # must keep a reference, or Qt will crash!
    __data = data or im.tobytes()
    return {
        'data': __data, 'im': im, 'format': format, 'colortable': colortable
    }

##
# An PIL image wrapper for Qt.  This is a subclass of PyQt's QImage
# class.
#
# @param im A PIL Image object, or a file name (given either as Python
#     string or a PyQt string object).

if qt_is_installed:
    class ImageQt(QImage):

        def __init__(self, im):
            im_data = _toqclass_helper(im)
            QImage.__init__(self,
                            im_data['data'], im_data['im'].size[0],
                            im_data['im'].size[1], im_data['format'])
            if im_data['colortable']:
                self.setColorTable(im_data['colortable'])


def toqimage(im):
    return ImageQt(im)


def toqpixmap(im):
    # # This doesn't work. For now using a dumb approach.
    # im_data = _toqclass_helper(im)
    # result = QPixmap(im_data['im'].size[0], im_data['im'].size[1])
    # result.loadFromData(im_data['data'])
    # Fix some strange bug that causes
    if im.mode == 'RGB':
        im = im.convert('RGBA')

    qimage = toqimage(im)
    return QPixmap.fromImage(qimage)
