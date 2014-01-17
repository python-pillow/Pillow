#
# The Python Imaging Library.
# $Id$
#
# kludge to get basic ImageFileIO functionality
#
# History:
# 1998-08-06 fl   Recreated
#
# Copyright (c) Secret Labs AB 1998-2002.
#
# See the README file for information on usage and redistribution.
#
"""
The **ImageFileIO** module can be used to read an image from a
socket, or any other stream device.

Deprecated. New code should use the :class:`PIL.ImageFile.Parser`
class in the :mod:`PIL.ImageFile` module instead.

.. seealso:: modules :class:`PIL.ImageFile.Parser`
"""

from io import BytesIO


class ImageFileIO(BytesIO):
    def __init__(self, fp):
        """
        Adds buffering to a stream file object, in order to
        provide **seek** and **tell** methods required
        by the :func:`PIL.Image.Image.open` method. The stream object must
        implement **read** and **close** methods.

        :param fp: Stream file handle.

        .. seealso:: modules :func:`PIL.Image.open`
        """
        data = fp.read()
        BytesIO.__init__(self, data)
