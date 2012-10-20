=======================
The PIL.ImageWin Module
=======================

The PIL.ImageWin Module
=======================

**Dib(image, size=None)** (class) [`# <#PIL.ImageWin.Dib-class>`_]
    Create a Windows bitmap with the given mode and size.

    For more information about this class, see `*The Dib
    Class* <#PIL.ImageWin.Dib-class>`_.

**HDC(dc)** (class) [`# <#PIL.ImageWin.HDC-class>`_]
    The ImageWin module contains support to create and display images
    under Windows 95/98, NT, 2000 and later.

    For more information about this class, see `*The HDC
    Class* <#PIL.ImageWin.HDC-class>`_.

**ImageWindow(image, title="PIL")** (class)
[`# <#PIL.ImageWin.ImageWindow-class>`_]
    Create an image window which displays the given image.

    For more information about this class, see `*The ImageWindow
    Class* <#PIL.ImageWin.ImageWindow-class>`_.

**Window(title="PIL", width=None, height=None)** (class)
[`# <#PIL.ImageWin.Window-class>`_]
    Create a Window with the given title size.

    For more information about this class, see `*The Window
    Class* <#PIL.ImageWin.Window-class>`_.

The Dib Class
-------------

**Dib(image, size=None)** (class) [`# <#PIL.ImageWin.Dib-class>`_]
    Create a Windows bitmap with the given mode and size. The mode can
    be one of "1", "L", "P", or "RGB". If the display requires a
    palette, this constructor creates a suitable palette and associates
    it with the image. For an "L" image, 128 greylevels are allocated.
    For an "RGB" image, a 6x6x6 colour cube is used, together with 20
    greylevels. To make sure that palettes work properly under Windows,
    you must call the **palette** method upon certain events from
    Windows.

**\_\_init\_\_(image, size=None)**
[`# <#PIL.ImageWin.Dib.__init__-method>`_]

    *image*
    *size*

**expose(handle)** [`# <#PIL.ImageWin.Dib.expose-method>`_]

    *handle*
        Device context (HDC), cast to a Python integer, or a HDC or HWND
        instance. In PythonWin, you can use the **GetHandleAttrib**
        method of the **CDC** class to get a suitable handle.

**frombytes(buffer)** [`# <#PIL.ImageWin.Dib.frombytes-method>`_]
    (For Python 2.6/2.7, this is also available as fromstring(buffer).)

    *buffer*
        A byte buffer containing display data (usually data returned
        from **tobytes**)

**paste(im, box=None)** [`# <#PIL.ImageWin.Dib.paste-method>`_]

    *im*
    *box*

**query\_palette(handle)**
[`# <#PIL.ImageWin.Dib.query_palette-method>`_]
    Installs the palette associated with the image in the given device
    context.

    This method should be called upon **QUERYNEWPALETTE** and
    **PALETTECHANGED** events from Windows. If this method returns a
    non-zero value, one or more display palette entries were changed,
    and the image should be redrawn.

    *handle*
    Returns:

**tobytes()** [`# <#PIL.ImageWin.Dib.tobytes-method>`_]

    Returns:

The HDC Class
-------------

**HDC(dc)** (class) [`# <#PIL.ImageWin.HDC-class>`_]
    The **ImageWin** module contains support to create and display
    images under Windows 95/98, NT, 2000 and later.

The ImageWindow Class
---------------------

**ImageWindow(image, title="PIL")** (class)
[`# <#PIL.ImageWin.ImageWindow-class>`_]

The Window Class
----------------

**Window(title="PIL", width=None, height=None)** (class)
[`# <#PIL.ImageWin.Window-class>`_]
