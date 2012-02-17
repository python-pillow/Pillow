========================
The PIL.ImageFile Module
========================

The PIL.ImageFile Module
========================

**\_ParserFile(data)** (class) [`# <#PIL.ImageFile._ParserFile-class>`_]
    (Internal) Support class for the Parser file.

    For more information about this class, see `*The \_ParserFile
    Class* <#PIL.ImageFile._ParserFile-class>`_.

**\_safe\_read(fp, size)** [`# <#PIL.ImageFile._safe_read-function>`_]

    *fp*
        File handle. Must implement a **read** method.
    *size*
    Returns:
        A string containing up to *size* bytes of data.

**\_save(im, fp, tile)** [`# <#PIL.ImageFile._save-function>`_]

    *im*
    *fp*
    *tile*

**ImageFile(fp=None, filename=None)** (class)
[`# <#PIL.ImageFile.ImageFile-class>`_]
    Base class for image file handlers.

    For more information about this class, see `*The ImageFile
    Class* <#PIL.ImageFile.ImageFile-class>`_.

**Parser** (class) [`# <#PIL.ImageFile.Parser-class>`_]
    Incremental image parser.

    For more information about this class, see `*The Parser
    Class* <#PIL.ImageFile.Parser-class>`_.

**StubImageFile** (class) [`# <#PIL.ImageFile.StubImageFile-class>`_]
    Base class for stub image loaders.

    For more information about this class, see `*The StubImageFile
    Class* <#PIL.ImageFile.StubImageFile-class>`_.

The \_ParserFile Class
----------------------

**\_ParserFile(data)** (class) [`# <#PIL.ImageFile._ParserFile-class>`_]
    (Internal) Support class for the **Parser** file.

The ImageFile Class
-------------------

**ImageFile(fp=None, filename=None)** (class)
[`# <#PIL.ImageFile.ImageFile-class>`_]

The Parser Class
----------------

**Parser** (class) [`# <#PIL.ImageFile.Parser-class>`_]
**close()** [`# <#PIL.ImageFile.Parser.close-method>`_]

    Returns:
    Raises **IOError**:

**feed(data)** [`# <#PIL.ImageFile.Parser.feed-method>`_]

    *data*
    Raises **IOError**:

**reset()** [`# <#PIL.ImageFile.Parser.reset-method>`_]

The StubImageFile Class
-----------------------

**StubImageFile** (class) [`# <#PIL.ImageFile.StubImageFile-class>`_]
    Base class for stub image loaders.

    A stub loader is an image loader that can identify files of a
    certain format, but relies on external code to load the file.

**\_load()** [`# <#PIL.ImageFile.StubImageFile._load-method>`_]
