========================
The PIL.ImageDraw Module
========================

The PIL.ImageDraw Module
========================

**Draw(im, mode=None)** [`# <#PIL.ImageDraw.Draw-function>`_]

    *im*
    *mode*

**getdraw(im=None, hints=None)**
[`# <#PIL.ImageDraw.getdraw-function>`_]

    *im*
    *hints*
    Returns:

**ImageDraw(im, mode=None)** (class)
[`# <#PIL.ImageDraw.ImageDraw-class>`_]
    A simple 2D drawing interface for PIL images.

    For more information about this class, see `*The ImageDraw
    Class* <#PIL.ImageDraw.ImageDraw-class>`_.

The ImageDraw Class
-------------------

**ImageDraw(im, mode=None)** (class)
[`# <#PIL.ImageDraw.ImageDraw-class>`_]
    A simple 2D drawing interface for PIL images.

    Application code should use the **Draw** factory, instead of
    directly.

**\_\_init\_\_(im, mode=None)**
[`# <#PIL.ImageDraw.ImageDraw.__init__-method>`_]

    *im*
    *mode*

**arc(xy, start, end, fill=None)**
[`# <#PIL.ImageDraw.ImageDraw.arc-method>`_]
**bitmap(xy, bitmap, fill=None)**
[`# <#PIL.ImageDraw.ImageDraw.bitmap-method>`_]
**chord(xy, start, end, fill=None, outline=None)**
[`# <#PIL.ImageDraw.ImageDraw.chord-method>`_]
**ellipse(xy, fill=None, outline=None)**
[`# <#PIL.ImageDraw.ImageDraw.ellipse-method>`_]
**getfont()** [`# <#PIL.ImageDraw.ImageDraw.getfont-method>`_]
**line(xy, fill=None, width=0)**
[`# <#PIL.ImageDraw.ImageDraw.line-method>`_]
**pieslice(xy, start, end, fill=None, outline=None)**
[`# <#PIL.ImageDraw.ImageDraw.pieslice-method>`_]
**point(xy, fill=None)** [`# <#PIL.ImageDraw.ImageDraw.point-method>`_]
**polygon(xy, fill=None, outline=None)**
[`# <#PIL.ImageDraw.ImageDraw.polygon-method>`_]
**rectangle(xy, fill=None, outline=None)**
[`# <#PIL.ImageDraw.ImageDraw.rectangle-method>`_]
**setfill(onoff)** [`# <#PIL.ImageDraw.ImageDraw.setfill-method>`_]
**setfont(font)** [`# <#PIL.ImageDraw.ImageDraw.setfont-method>`_]
**setink(ink)** [`# <#PIL.ImageDraw.ImageDraw.setink-method>`_]
**shape(shape, fill=None, outline=None)**
[`# <#PIL.ImageDraw.ImageDraw.shape-method>`_]
**text(xy, text, fill=None, font=None, anchor=None)**
[`# <#PIL.ImageDraw.ImageDraw.text-method>`_]
**textsize(text, font=None)**
[`# <#PIL.ImageDraw.ImageDraw.textsize-method>`_]
