========================
The PIL.ImageFont Module
========================

The PIL.ImageFont Module
========================

**FreeTypeFont(file, size, index=0, encoding="")** (class)
[`# <#PIL.ImageFont.FreeTypeFont-class>`_]
    Wrapper for FreeType fonts.

    For more information about this class, see `*The FreeTypeFont
    Class* <#PIL.ImageFont.FreeTypeFont-class>`_.

**ImageFont** (class) [`# <#PIL.ImageFont.ImageFont-class>`_]
    The ImageFont module defines a class with the same name.

    For more information about this class, see `*The ImageFont
    Class* <#PIL.ImageFont.ImageFont-class>`_.

**load(filename)** [`# <#PIL.ImageFont.load-function>`_]

    *filename*
    Returns:
    Raises **IOError**:

**load\_default()** [`# <#PIL.ImageFont.load_default-function>`_]

    Returns:

**load\_path(filename)** [`# <#PIL.ImageFont.load_path-function>`_]

    *filename*
    Returns:
    Raises **IOError**:

**TransposedFont(font, orientation=None)** (class)
[`# <#PIL.ImageFont.TransposedFont-class>`_]
    Wrapper that creates a transposed font from any existing font
    object.

    *font*
    *orientation*

    For more information about this class, see `*The TransposedFont
    Class* <#PIL.ImageFont.TransposedFont-class>`_.

**truetype(filename, size, index=0, encoding="")**
[`# <#PIL.ImageFont.truetype-function>`_]
    Load a TrueType or OpenType font file, and create a font object.
    This function loads a font object from the given file, and creates a
    font object for a font of the given size.

    This function requires the \_imagingft service.

    *filename*
        A truetype font file. Under Windows, if the file is not found in
        this filename, the loader also looks in Windows **fonts**
        directory
    *size*
    *index*
    *encoding*
    Returns:
    Raises **IOError**:

The FreeTypeFont Class
----------------------

**FreeTypeFont(file, size, index=0, encoding="")** (class)
[`# <#PIL.ImageFont.FreeTypeFont-class>`_]
    Wrapper for FreeType fonts. Application code should use the
    **truetype** factory function to create font objects.

The ImageFont Class
-------------------

**ImageFont** (class) [`# <#PIL.ImageFont.ImageFont-class>`_]
    The **ImageFont** module defines a class with the same name.
    Instances of this class store bitmap fonts, and are used with the
    **text** method of the **ImageDraw** class.

    PIL uses it's own font file format to store bitmap fonts. You can
    use the **pilfont** utility to convert BDF and PCF font descriptors
    (X window font formats) to this format.

    Starting with version 1.1.4, PIL can be configured to support
    TrueType and OpenType fonts. For earlier version, TrueType support
    is only available as part of the imToolkit package

The TransposedFont Class
------------------------

**TransposedFont(font, orientation=None)** (class)
[`# <#PIL.ImageFont.TransposedFont-class>`_]

    *font*
    *orientation*

