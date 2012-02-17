==========================
The PIL.ImageFilter Module
==========================

The PIL.ImageFilter Module
==========================

**BLUR** (class) [`# <#PIL.ImageFilter.BLUR-class>`_]
    Blur filter.

    For more information about this class, see `*The BLUR
    Class* <#PIL.ImageFilter.BLUR-class>`_.

**CONTOUR** (class) [`# <#PIL.ImageFilter.CONTOUR-class>`_]
    Contour filter.

    For more information about this class, see `*The CONTOUR
    Class* <#PIL.ImageFilter.CONTOUR-class>`_.

**DETAIL** (class) [`# <#PIL.ImageFilter.DETAIL-class>`_]
    Detail filter.

    For more information about this class, see `*The DETAIL
    Class* <#PIL.ImageFilter.DETAIL-class>`_.

**EDGE\_ENHANCE** (class) [`# <#PIL.ImageFilter.EDGE_ENHANCE-class>`_]
    Edge enhancement filter.

    For more information about this class, see `*The EDGE\_ENHANCE
    Class* <#PIL.ImageFilter.EDGE_ENHANCE-class>`_.

**EDGE\_ENHANCE\_MORE** (class)
[`# <#PIL.ImageFilter.EDGE_ENHANCE_MORE-class>`_]
    Stronger edge enhancement filter.

    For more information about this class, see `*The EDGE\_ENHANCE\_MORE
    Class* <#PIL.ImageFilter.EDGE_ENHANCE_MORE-class>`_.

**EMBOSS** (class) [`# <#PIL.ImageFilter.EMBOSS-class>`_]
    Embossing filter.

    For more information about this class, see `*The EMBOSS
    Class* <#PIL.ImageFilter.EMBOSS-class>`_.

**FIND\_EDGES** (class) [`# <#PIL.ImageFilter.FIND_EDGES-class>`_]
    Edge-finding filter.

    For more information about this class, see `*The FIND\_EDGES
    Class* <#PIL.ImageFilter.FIND_EDGES-class>`_.

**Kernel(size, kernel, \*\*options)** (class)
[`# <#PIL.ImageFilter.Kernel-class>`_]
    Convolution filter kernel.

    For more information about this class, see `*The Kernel
    Class* <#PIL.ImageFilter.Kernel-class>`_.

**MaxFilter(size=3)** (class) [`# <#PIL.ImageFilter.MaxFilter-class>`_]
    Max filter.

    For more information about this class, see `*The MaxFilter
    Class* <#PIL.ImageFilter.MaxFilter-class>`_.

**MedianFilter(size=3)** (class)
[`# <#PIL.ImageFilter.MedianFilter-class>`_]
    Median filter.

    For more information about this class, see `*The MedianFilter
    Class* <#PIL.ImageFilter.MedianFilter-class>`_.

**MinFilter(size=3)** (class) [`# <#PIL.ImageFilter.MinFilter-class>`_]
    Min filter.

    For more information about this class, see `*The MinFilter
    Class* <#PIL.ImageFilter.MinFilter-class>`_.

**ModeFilter(size=3)** (class)
[`# <#PIL.ImageFilter.ModeFilter-class>`_]
    Mode filter.

    For more information about this class, see `*The ModeFilter
    Class* <#PIL.ImageFilter.ModeFilter-class>`_.

**RankFilter(size, rank)** (class)
[`# <#PIL.ImageFilter.RankFilter-class>`_]
    Rank filter.

    For more information about this class, see `*The RankFilter
    Class* <#PIL.ImageFilter.RankFilter-class>`_.

**SHARPEN** (class) [`# <#PIL.ImageFilter.SHARPEN-class>`_]
    Sharpening filter.

    For more information about this class, see `*The SHARPEN
    Class* <#PIL.ImageFilter.SHARPEN-class>`_.

**SMOOTH** (class) [`# <#PIL.ImageFilter.SMOOTH-class>`_]
    Smoothing filter.

    For more information about this class, see `*The SMOOTH
    Class* <#PIL.ImageFilter.SMOOTH-class>`_.

**SMOOTH\_MORE** (class) [`# <#PIL.ImageFilter.SMOOTH_MORE-class>`_]
    Stronger smoothing filter.

    For more information about this class, see `*The SMOOTH\_MORE
    Class* <#PIL.ImageFilter.SMOOTH_MORE-class>`_.

The BLUR Class
--------------

**BLUR** (class) [`# <#PIL.ImageFilter.BLUR-class>`_]

The CONTOUR Class
-----------------

**CONTOUR** (class) [`# <#PIL.ImageFilter.CONTOUR-class>`_]

The DETAIL Class
----------------

**DETAIL** (class) [`# <#PIL.ImageFilter.DETAIL-class>`_]

The EDGE\_ENHANCE Class
-----------------------

**EDGE\_ENHANCE** (class) [`# <#PIL.ImageFilter.EDGE_ENHANCE-class>`_]

The EDGE\_ENHANCE\_MORE Class
-----------------------------

**EDGE\_ENHANCE\_MORE** (class)
[`# <#PIL.ImageFilter.EDGE_ENHANCE_MORE-class>`_]

The EMBOSS Class
----------------

**EMBOSS** (class) [`# <#PIL.ImageFilter.EMBOSS-class>`_]

The FIND\_EDGES Class
---------------------

**FIND\_EDGES** (class) [`# <#PIL.ImageFilter.FIND_EDGES-class>`_]

The Kernel Class
----------------

**Kernel(size, kernel, \*\*options)** (class)
[`# <#PIL.ImageFilter.Kernel-class>`_]
**\_\_init\_\_(size, kernel, \*\*options)**
[`# <#PIL.ImageFilter.Kernel.__init__-method>`_]
    Create a convolution kernel. The current version only supports 3x3
    and 5x5 integer and floating point kernels.

    In the current version, kernels can only be applied to "L" and "RGB"
    images.

    *size*
    *kernel*
    *\*\*options*
    *scale=*
    *offset=*

The MaxFilter Class
-------------------

**MaxFilter(size=3)** (class) [`# <#PIL.ImageFilter.MaxFilter-class>`_]
**\_\_init\_\_(size=3)**
[`# <#PIL.ImageFilter.MaxFilter.__init__-method>`_]

    *size*

The MedianFilter Class
----------------------

**MedianFilter(size=3)** (class)
[`# <#PIL.ImageFilter.MedianFilter-class>`_]
**\_\_init\_\_(size=3)**
[`# <#PIL.ImageFilter.MedianFilter.__init__-method>`_]

    *size*

The MinFilter Class
-------------------

**MinFilter(size=3)** (class) [`# <#PIL.ImageFilter.MinFilter-class>`_]
**\_\_init\_\_(size=3)**
[`# <#PIL.ImageFilter.MinFilter.__init__-method>`_]

    *size*

The ModeFilter Class
--------------------

**ModeFilter(size=3)** (class)
[`# <#PIL.ImageFilter.ModeFilter-class>`_]
**\_\_init\_\_(size=3)**
[`# <#PIL.ImageFilter.ModeFilter.__init__-method>`_]

    *size*

The RankFilter Class
--------------------

**RankFilter(size, rank)** (class)
[`# <#PIL.ImageFilter.RankFilter-class>`_]
**\_\_init\_\_(size, rank)**
[`# <#PIL.ImageFilter.RankFilter.__init__-method>`_]

    *size*
    *rank*

The SHARPEN Class
-----------------

**SHARPEN** (class) [`# <#PIL.ImageFilter.SHARPEN-class>`_]

The SMOOTH Class
----------------

**SMOOTH** (class) [`# <#PIL.ImageFilter.SMOOTH-class>`_]

The SMOOTH\_MORE Class
----------------------

**SMOOTH\_MORE** (class) [`# <#PIL.ImageFilter.SMOOTH_MORE-class>`_]
