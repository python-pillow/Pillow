======================
The PIL.ImageTk Module
======================

The PIL.ImageTk Module
======================

The **ImageTk** module contains support to create and modify Tkinter
**BitmapImage** and **PhotoImage** objects.

For examples, see the demo programs in the *Scripts* directory.

Module Contents
---------------

**BitmapImage(image=None, \*\*options)** (class)
[`# <#PIL.ImageTk.BitmapImage-class>`_]
    Create a Tkinter-compatible bitmap image.

    For more information about this class, see `*The BitmapImage
    Class* <#PIL.ImageTk.BitmapImage-class>`_.

**getimage(photo)** [`# <#PIL.ImageTk.getimage-function>`_]
**PhotoImage(image=None, size=None, \*\*options)** (class)
[`# <#PIL.ImageTk.PhotoImage-class>`_]
    Creates a Tkinter-compatible photo image.

    For more information about this class, see `*The PhotoImage
    Class* <#PIL.ImageTk.PhotoImage-class>`_.

The BitmapImage Class
---------------------

**BitmapImage(image=None, \*\*options)** (class)
[`# <#PIL.ImageTk.BitmapImage-class>`_]
**\_\_init\_\_(image=None, \*\*options)**
[`# <#PIL.ImageTk.BitmapImage.__init__-method>`_]
    Create a Tkinter-compatible bitmap image.

    The given image must have mode "1". Pixels having value 0 are
    treated as transparent. Options, if any, are passed on to Tkinter.
    The most commonly used option is **foreground**, which is used to
    specify the colour for the non-transparent parts. See the Tkinter
    documentation for information on how to specify colours.

    *image*

**\_\_str\_\_()** [`# <#PIL.ImageTk.BitmapImage.__str__-method>`_]

    Returns:

**height()** [`# <#PIL.ImageTk.BitmapImage.height-method>`_]

    Returns:

**width()** [`# <#PIL.ImageTk.BitmapImage.width-method>`_]

    Returns:

The PhotoImage Class
--------------------

**PhotoImage(image=None, size=None, \*\*options)** (class)
[`# <#PIL.ImageTk.PhotoImage-class>`_]
**\_\_init\_\_(image=None, size=None, \*\*options)**
[`# <#PIL.ImageTk.PhotoImage.__init__-method>`_]
    Create a photo image object. The constructor takes either a PIL
    image, or a mode and a size. Alternatively, you can use the **file**
    or **data** options to initialize the photo image object.

    *image*
    *size*
    *file=*
    *data=*

**\_\_str\_\_()** [`# <#PIL.ImageTk.PhotoImage.__str__-method>`_]

    Returns:

**height()** [`# <#PIL.ImageTk.PhotoImage.height-method>`_]

    Returns:

**paste(im, box=None)** [`# <#PIL.ImageTk.PhotoImage.paste-method>`_]

    *im*
    *box*

**width()** [`# <#PIL.ImageTk.PhotoImage.width-method>`_]

    Returns:

