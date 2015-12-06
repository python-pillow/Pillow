.. py:module:: PIL.OleFileIO
.. py:currentmodule:: PIL.OleFileIO

:py:mod:`OleFileIO` Module
===========================

The :py:mod:`OleFileIO` module reads Microsoft OLE2 files (also called
Structured Storage or Microsoft Compound Document File Format), such
as Microsoft Office documents, Image Composer and FlashPix files, and
Outlook messages.

This module is the `OleFileIO\_PL`_ project by Philippe Lagadec, v0.42,
merged back into Pillow.

.. _OleFileIO\_PL: http://www.decalage.info/python/olefileio

How to use this module
----------------------

For more information, see also the file **PIL/OleFileIO.py**, sample
code at the end of the module itself, and docstrings within the code.

About the structure of OLE files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An OLE file can be seen as a mini file system or a Zip archive: It
contains **streams** of data that look like files embedded within the
OLE file. Each stream has a name. For example, the main stream of a MS
Word document containing its text is named "WordDocument".

An OLE file can also contain **storages**. A storage is a folder that
contains streams or other storages. For example, a MS Word document with
VBA macros has a storage called "Macros".

Special streams can contain **properties**. A property is a specific
value that can be used to store information such as the metadata of a
document (title, author, creation date, etc). Property stream names
usually start with the character '05'.

For example, a typical MS Word document may look like this:

::

    \x05DocumentSummaryInformation (stream)
    \x05SummaryInformation (stream)
    WordDocument (stream)
    Macros (storage)
        PROJECT (stream)
        PROJECTwm (stream)
        VBA (storage)
            Module1 (stream)
            ThisDocument (stream)
            _VBA_PROJECT (stream)
            dir (stream)
    ObjectPool (storage)

Test if a file is an OLE container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use isOleFile to check if the first bytes of the file contain the Magic
for OLE files, before opening it. isOleFile returns True if it is an OLE
file, False otherwise.

.. code-block:: python

        assert OleFileIO.isOleFile('myfile.doc')

Open an OLE file from disk
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create an OleFileIO object with the file path as parameter:

.. code-block:: python

        ole = OleFileIO.OleFileIO('myfile.doc')

Open an OLE file from a file-like object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is useful if the file is not on disk, e.g. already stored in a
string or as a file-like object.

.. code-block:: python

        ole = OleFileIO.OleFileIO(f)

For example the code below reads a file into a string, then uses BytesIO
to turn it into a file-like object.

.. code-block:: python

        data = open('myfile.doc', 'rb').read()
        f = io.BytesIO(data) # or StringIO.StringIO for Python 2.x
        ole = OleFileIO.OleFileIO(f)

How to handle malformed OLE files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the parser is configured to be as robust and permissive as
possible, allowing to parse most malformed OLE files. Only fatal errors
will raise an exception. It is possible to tell the parser to be more
strict in order to raise exceptions for files that do not fully conform
to the OLE specifications, using the raise\_defect option:

.. code-block:: python

        ole = OleFileIO.OleFileIO('myfile.doc', raise_defects=DEFECT_INCORRECT)

When the parsing is done, the list of non-fatal issues detected is
available as a list in the parsing\_issues attribute of the OleFileIO
object:

.. code-block:: python

        print('Non-fatal issues raised during parsing:')
        if ole.parsing_issues:
            for exctype, msg in ole.parsing_issues:
                print('- %s: %s' % (exctype.__name__, msg))
        else:
            print('None')

Syntax for stream and storage path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two different syntaxes are allowed for methods that need or return the
path of streams and storages:

1) Either a **list of strings** including all the storages from the root
   up to the stream/storage name. For example a stream called
   "WordDocument" at the root will have ['WordDocument'] as full path. A
   stream called "ThisDocument" located in the storage "Macros/VBA" will
   be ['Macros', 'VBA', 'ThisDocument']. This is the original syntax
   from PIL. While hard to read and not very convenient, this syntax
   works in all cases.

2) Or a **single string with slashes** to separate storage and stream
   names (similar to the Unix path syntax). The previous examples would
   be 'WordDocument' and 'Macros/VBA/ThisDocument'. This syntax is
   easier, but may fail if a stream or storage name contains a slash.

Both are case-insensitive.

Switching between the two is easy:

.. code-block:: python

        slash_path = '/'.join(list_path)
        list_path  = slash_path.split('/')

Get the list of streams
~~~~~~~~~~~~~~~~~~~~~~~

listdir() returns a list of all the streams contained in the OLE file,
including those stored in storages. Each stream is listed itself as a
list, as described above.

.. code-block:: python

        print(ole.listdir())

Sample result:

.. code-block:: python

        [['\x01CompObj'], ['\x05DocumentSummaryInformation'], ['\x05SummaryInformation']
        , ['1Table'], ['Macros', 'PROJECT'], ['Macros', 'PROJECTwm'], ['Macros', 'VBA',
        'Module1'], ['Macros', 'VBA', 'ThisDocument'], ['Macros', 'VBA', '_VBA_PROJECT']
        , ['Macros', 'VBA', 'dir'], ['ObjectPool'], ['WordDocument']]

As an option it is possible to choose if storages should also be listed,
with or without streams:

.. code-block:: python

        ole.listdir (streams=False, storages=True)

Test if known streams/storages exist:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

exists(path) checks if a given stream or storage exists in the OLE file.

.. code-block:: python

        if ole.exists('worddocument'):
            print("This is a Word document.")
            if ole.exists('macros/vba'):
                 print("This document seems to contain VBA macros.")

Read data from a stream
~~~~~~~~~~~~~~~~~~~~~~~

openstream(path) opens a stream as a file-like object.

The following example extracts the "Pictures" stream from a PPT file:

.. code-block:: python

        pics = ole.openstream('Pictures')
        data = pics.read()


Get information about a stream/storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several methods can provide the size, type and timestamps of a given
stream/storage:

get\_size(path) returns the size of a stream in bytes:

.. code-block:: python

        s = ole.get_size('WordDocument')

get\_type(path) returns the type of a stream/storage, as one of the
following constants: STGTY\_STREAM for a stream, STGTY\_STORAGE for a
storage, STGTY\_ROOT for the root entry, and False for a non existing
path.

.. code-block:: python

        t = ole.get_type('WordDocument')

get\_ctime(path) and get\_mtime(path) return the creation and
modification timestamps of a stream/storage, as a Python datetime object
with UTC timezone. Please note that these timestamps are only present if
the application that created the OLE file explicitly stored them, which
is rarely the case. When not present, these methods return None.

.. code-block:: python

        c = ole.get_ctime('WordDocument')
        m = ole.get_mtime('WordDocument')

The root storage is a special case: You can get its creation and
modification timestamps using the OleFileIO.root attribute:

.. code-block:: python

        c = ole.root.getctime()
        m = ole.root.getmtime()

Extract metadata
~~~~~~~~~~~~~~~~

get\_metadata() will check if standard property streams exist, parse all
the properties they contain, and return an OleMetadata object with the
found properties as attributes.

.. code-block:: python

        meta = ole.get_metadata()
        print('Author:', meta.author)
        print('Title:', meta.title)
        print('Creation date:', meta.create_time)
        # print all metadata:
        meta.dump()

Available attributes include:

::

    codepage, title, subject, author, keywords, comments, template,
    last_saved_by, revision_number, total_edit_time, last_printed, create_time,
    last_saved_time, num_pages, num_words, num_chars, thumbnail,
    creating_application, security, codepage_doc, category, presentation_target,
    bytes, lines, paragraphs, slides, notes, hidden_slides, mm_clips,
    scale_crop, heading_pairs, titles_of_parts, manager, company, links_dirty,
    chars_with_spaces, unused, shared_doc, link_base, hlinks, hlinks_changed,
    version, dig_sig, content_type, content_status, language, doc_version

See the source code of the OleMetadata class for more information.

Parse a property stream
~~~~~~~~~~~~~~~~~~~~~~~

get\_properties(path) can be used to parse any property stream that is
not handled by get\_metadata. It returns a dictionary indexed by
integers. Each integer is the index of the property, pointing to its
value. For example in the standard property stream
'05SummaryInformation', the document title is property #2, and the
subject is #3.

.. code-block:: python

        p = ole.getproperties('specialprops')

By default as in the original PIL version, timestamp properties are
converted into a number of seconds since Jan 1,1601. With the option
convert\_time, you can obtain more convenient Python datetime objects
(UTC timezone). If some time properties should not be converted (such as
total editing time in '05SummaryInformation'), the list of indexes can
be passed as no\_conversion:

.. code-block:: python

        p = ole.getproperties('specialprops', convert_time=True, no_conversion=[10])

Close the OLE file
~~~~~~~~~~~~~~~~~~

Unless your application is a simple script that terminates after
processing an OLE file, do not forget to close each OleFileIO object
after parsing to close the file on disk.

.. code-block:: python

        ole.close()

Use OleFileIO as a script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OleFileIO can also be used as a script from the command-line to
display the structure of an OLE file and its metadata, for example:

::

    PIL/OleFileIO.py myfile.doc

You can use the option -c to check that all streams can be read fully,
and -d to generate very verbose debugging information.

How to contribute
-----------------

The code is available in `a Mercurial repository on
bitbucket <https://bitbucket.org/decalage/olefileio_pl>`_. You may use
it to submit enhancements or to report any issue.

If you would like to help us improve this module, or simply provide
feedback, please `contact me <http://decalage.info/contact>`_. You can
help in many ways:

-  test this module on different platforms / Python versions
-  find and report bugs
-  improve documentation, code samples, docstrings
-  write unittest test cases
-  provide tricky malformed files

How to report bugs
------------------

To report a bug, for example a normal file which is not parsed
correctly, please use the `issue reporting
page <https://bitbucket.org/decalage/olefileio_pl/issues?status=new&status=open>`_,
or if you prefer to do it privately, use this `contact
form <http://decalage.info/contact>`_. Please provide all the
information about the context and how to reproduce the bug.

If possible please join the debugging output of OleFileIO. For this,
launch the following command :

::

    PIL/OleFileIO.py -d -c file >debug.txt


Classes and Methods
-------------------

.. automodule:: PIL.OleFileIO
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:
