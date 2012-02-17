==========================
The PIL.ImageFileIO Module
==========================

The PIL.ImageFileIO Module
==========================

**ImageFileIO(fp)** (class) [`# <#PIL.ImageFileIO.ImageFileIO-class>`_]
    The ImageFileIO module can be used to read an image from a socket,
    or any other stream device.

    For more information about this class, see `*The ImageFileIO
    Class* <#PIL.ImageFileIO.ImageFileIO-class>`_.

The ImageFileIO Class
---------------------

**ImageFileIO(fp)** (class) [`# <#PIL.ImageFileIO.ImageFileIO-class>`_]
    The **ImageFileIO** module can be used to read an image from a
    socket, or any other stream device.

    This module is deprecated. New code should use the **Parser** class
    in the `ImageFile <imagefile>`_ module instead.

**\_\_init\_\_(fp)**
[`# <#PIL.ImageFileIO.ImageFileIO.__init__-method>`_]
    Adds buffering to a stream file object, in order to provide **seek**
    and **tell** methods required by the **Image.open** method. The
    stream object must implement **read** and **close** methods.

    *fp*

