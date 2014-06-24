OleFileIO_PL
============

[OleFileIO_PL](http://www.decalage.info/python/olefileio) is a Python module to parse and read [Microsoft OLE2 files (also called Structured Storage, Compound File Binary Format or Compound Document File Format)](http://en.wikipedia.org/wiki/Compound_File_Binary_Format), such as Microsoft Office documents, Image Composer and FlashPix files, Outlook messages, StickyNotes, several Microscopy file formats ...

This is an improved version of the OleFileIO module from [PIL](http://www.pythonware.com/products/pil/index.htm), the excellent Python Imaging Library, created and maintained by Fredrik Lundh. The API is still compatible with PIL, but since 2005 I have improved the internal implementation significantly, with new features, bugfixes and a more robust design.

As far as I know, this module is now the most complete and robust Python implementation to read MS OLE2 files, portable on several operating systems. (please tell me if you know other similar Python modules)

OleFileIO_PL can be used as an independent module or with PIL. The goal is to have it integrated into [Pillow](http://python-pillow.github.io/), the friendly fork of PIL.

OleFileIO\_PL is mostly meant for developers. If you are looking for tools to analyze OLE files or to extract data, then please also check [python-oletools](http://www.decalage.info/python/oletools), which are built upon OleFileIO_PL.

News
----

Follow all updates and news on Twitter: <https://twitter.com/decalage2>

- **2014-02-04 v0.30**: now compatible with Python 3.x, thanks to Martin Panter who did most of the hard work.
- 2013-07-24 v0.26: added methods to parse stream/storage timestamps, improved listdir to include storages, fixed parsing of direntry timestamps
- 2013-05-27 v0.25: improved metadata extraction, properties parsing and exception handling, fixed [issue #12](https://bitbucket.org/decalage/olefileio_pl/issue/12/error-when-converting-timestamps-in-ole)
- 2013-05-07 v0.24: new features to extract metadata (get\_metadata method and OleMetadata class), improved getproperties to convert timestamps to Python datetime
- 2012-10-09: published [python-oletools](http://www.decalage.info/python/oletools), a package of analysis tools based on OleFileIO_PL
- 2012-09-11 v0.23: added support for file-like objects, fixed [issue #8](https://bitbucket.org/decalage/olefileio_pl/issue/8/bug-with-file-object)
- 2012-02-17 v0.22: fixed issues #7 (bug in getproperties) and #2 (added close method)
- 2011-10-20: code hosted on bitbucket to ease contributions and bug tracking
- 2010-01-24 v0.21: fixed support for big-endian CPUs, such as PowerPC Macs.
- 2009-12-11 v0.20: small bugfix in OleFileIO.open when filename is not plain str.
- 2009-12-10 v0.19: fixed support for 64 bits platforms (thanks to Ben G. and Martijn for reporting the bug)
- see changelog in source code for more info.

Download
--------

The archive is available on [the project page](https://bitbucket.org/decalage/olefileio_pl/downloads).

Features
--------

- Parse and read any OLE file such as Microsoft Office 97-2003 legacy document formats (Word .doc, Excel .xls, PowerPoint .ppt, Visio .vsd, Project .mpp), Image Composer and FlashPix files, Outlook messages, StickyNotes, Zeiss AxioVision ZVI files, Olympus FluoView OIB files, ...
- List all the streams and storages contained in an OLE file
- Open streams as files
- Parse and read property streams, containing metadata of the file
- Portable, pure Python module, no dependency


Main improvements over the original version of OleFileIO in PIL:
----------------------------------------------------------------

- Compatible with Python 3.x and 2.6+
- Many bug fixes
- Support for files larger than 6.8MB
- Support for 64 bits platforms and big-endian CPUs
- Robust: many checks to detect malformed files
- Runtime option to choose if malformed files should be parsed or raise exceptions
- Improved API
- Metadata extraction, stream/storage timestamps (e.g. for document forensics)
- Can open file-like objects
- Added setup.py and install.bat to ease installation
- More convenient slash-based syntax for stream paths



How to use this module
----------------------

OleFileIO_PL can be used as an independent module or with PIL. The main functions and methods are explained below.

For more information, see also the file **OleFileIO_PL.html**, sample code at the end of the module itself, and docstrings within the code.

### About the structure of OLE files ###

An OLE file can be seen as a mini file system or a Zip archive: It contains **streams** of data that look like files embedded within the OLE file. Each stream has a name. For example, the main stream of a MS Word document containing its text is named "WordDocument".

An OLE file can also contain **storages**. A storage is a folder that contains streams or other storages. For example, a MS Word document with VBA macros has a storage called "Macros".

Special streams can contain **properties**. A property is a specific value that can be used to store information such as the metadata of a document (title, author, creation date, etc). Property stream names usually start with the character '\x05'.

For example, a typical MS Word document may look like this:

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



### Import OleFileIO_PL ###

	:::python
		import OleFileIO_PL

As of version 0.30, the code has been changed to be compatible with Python 3.x. As a consequence, compatibility with Python 2.5 or older is not provided anymore. However, a copy of v0.26 is available as OleFileIO_PL2.py. If your application needs to be compatible with Python 2.5 or older, you may use the following code to load the old version when needed:

	:::python
		try:
			import OleFileIO_PL
		except:
			import OleFileIO_PL2 as OleFileIO_PL

If you think OleFileIO_PL should stay compatible with Python 2.5 or older, please [contact me](http://decalage.info/contact).


### Test if a file is an OLE container ###

Use isOleFile to check if the first bytes of the file contain the Magic for OLE files, before opening it. isOleFile returns True if it is an OLE file, False otherwise (new in v0.16).

	:::python
		assert OleFileIO_PL.isOleFile('myfile.doc')


### Open an OLE file from disk ###

Create an OleFileIO object with the file path as parameter:

	:::python
		ole = OleFileIO_PL.OleFileIO('myfile.doc')

### Open an OLE file from a file-like object ###

This is useful if the file is not on disk, e.g. already stored in a string or as a file-like object.

	:::python
		ole = OleFileIO_PL.OleFileIO(f)

For example the code below reads a file into a string, then uses BytesIO to turn it into a file-like object.

	:::python
		data = open('myfile.doc', 'rb').read()
		f = io.BytesIO(data) # or StringIO.StringIO for Python 2.x
		ole = OleFileIO_PL.OleFileIO(f)

### How to handle malformed OLE files ###

By default, the parser is configured to be as robust and permissive as possible, allowing to parse most malformed OLE files. Only fatal errors will raise an exception. It is possible to tell the parser to be more strict in order to raise exceptions for files that do not fully conform to the OLE specifications, using the raise_defect option (new in v0.14):

	:::python
		ole = OleFileIO_PL.OleFileIO('myfile.doc', raise_defects=DEFECT_INCORRECT)

When the parsing is done, the list of non-fatal issues detected is available as a list in the parsing_issues attribute of the OleFileIO object (new in 0.25):

	:::python
        print('Non-fatal issues raised during parsing:')
        if ole.parsing_issues:
            for exctype, msg in ole.parsing_issues:
                print('- %s: %s' % (exctype.__name__, msg))
        else:
            print('None')


### Syntax for stream and storage path ###

Two different syntaxes are allowed for methods that need or return the path of streams and storages:

1) Either a **list of strings** including all the storages from the root up to the stream/storage name. For example a stream called "WordDocument" at the root will have ['WordDocument'] as full path. A stream called "ThisDocument" located in the storage "Macros/VBA" will be ['Macros', 'VBA', 'ThisDocument']. This is the original syntax from PIL. While hard to read and not very convenient, this syntax works in all cases.

2) Or a **single string with slashes** to separate storage and stream names (similar to the Unix path syntax). The previous examples would be 'WordDocument' and 'Macros/VBA/ThisDocument'. This syntax is easier, but may fail if a stream or storage name contains a slash. (new in v0.15)

Both are case-insensitive.

Switching between the two is easy:

	:::python
		slash_path = '/'.join(list_path)
		list_path  = slash_path.split('/')


### Get the list of streams ###

listdir() returns a list of all the streams contained in the OLE file, including those stored in storages. Each stream is listed itself as a list, as described above.

	:::python
		print(ole.listdir())

Sample result:

	:::python
		[['\x01CompObj'], ['\x05DocumentSummaryInformation'], ['\x05SummaryInformation']
		, ['1Table'], ['Macros', 'PROJECT'], ['Macros', 'PROJECTwm'], ['Macros', 'VBA',
		'Module1'], ['Macros', 'VBA', 'ThisDocument'], ['Macros', 'VBA', '_VBA_PROJECT']
		, ['Macros', 'VBA', 'dir'], ['ObjectPool'], ['WordDocument']]

As an option it is possible to choose if storages should also be listed, with or without streams (new in v0.26):

	:::python
		ole.listdir (streams=False, storages=True)


### Test if known streams/storages exist: ###

exists(path) checks if a given stream or storage exists in the OLE file (new in v0.16).

	:::python
		if ole.exists('worddocument'):
		    print("This is a Word document.")
		    if ole.exists('macros/vba'):
		         print("This document seems to contain VBA macros.")


### Read data from a stream ###

openstream(path) opens a stream as a file-like object.

The following example extracts the "Pictures" stream from a PPT file:

	:::python
	    pics = ole.openstream('Pictures')
	    data = pics.read()


### Get information about a stream/storage ###

Several methods can provide the size, type and timestamps of a given stream/storage:

get_size(path) returns the size of a stream in bytes (new in v0.16):

	:::python
		s = ole.get_size('WordDocument')

get_type(path) returns the type of a stream/storage, as one of the following constants: STGTY\_STREAM for a stream, STGTY\_STORAGE for a storage, STGTY\_ROOT for the root entry, and False for a non existing path (new in v0.15).

	:::python
		t = ole.get_type('WordDocument')

get\_ctime(path) and get\_mtime(path) return the creation and modification timestamps of a stream/storage, as a Python datetime object with UTC timezone. Please note that these timestamps are only present if the application that created the OLE file explicitly stored them, which is rarely the case. When not present, these methods return None (new in v0.26).

	:::python
		c = ole.get_ctime('WordDocument')
		m = ole.get_mtime('WordDocument')

The root storage is a special case: You can get its creation and modification timestamps using the OleFileIO.root attribute (new in v0.26):

	:::python
		c = ole.root.getctime()
		m = ole.root.getmtime()

### Extract metadata ###

get_metadata() will check if standard property streams exist, parse all the properties they contain, and return an OleMetadata object with the found properties as attributes (new in v0.24).

	:::python
		meta = ole.get_metadata()
		print('Author:', meta.author)
		print('Title:', meta.title)
		print('Creation date:', meta.create_time)
		# print all metadata:
		meta.dump()

Available attributes include:

    codepage, title, subject, author, keywords, comments, template,
    last_saved_by, revision_number, total_edit_time, last_printed, create_time,
    last_saved_time, num_pages, num_words, num_chars, thumbnail,
    creating_application, security, codepage_doc, category, presentation_target,
    bytes, lines, paragraphs, slides, notes, hidden_slides, mm_clips,
    scale_crop, heading_pairs, titles_of_parts, manager, company, links_dirty,
    chars_with_spaces, unused, shared_doc, link_base, hlinks, hlinks_changed,
    version, dig_sig, content_type, content_status, language, doc_version

See the source code of the OleMetadata class for more information.


### Parse a property stream ###

get\_properties(path) can be used to parse any property stream that is not handled by get\_metadata. It returns a dictionary indexed by integers. Each integer is the index of the property, pointing to its value. For example in the standard property stream '\x05SummaryInformation', the document title is property #2, and the subject is #3.

	:::python
		p = ole.getproperties('specialprops')

By default as in the original PIL version, timestamp properties are converted into a number of seconds since Jan 1,1601. With the option convert\_time, you can obtain more convenient Python datetime objects (UTC timezone). If some time properties should not be converted (such as total editing time in '\x05SummaryInformation'), the list of indexes can be passed as no_conversion (new in v0.25):

	:::python
		p = ole.getproperties('specialprops', convert_time=True, no_conversion=[10])


### Close the OLE file ###

Unless your application is a simple script that terminates after processing an OLE file, do not forget to close each OleFileIO object after parsing to close the file on disk. (new in v0.22)

	:::python
		ole.close()

### Use OleFileIO_PL as a script ###

OleFileIO_PL can also be used as a script from the command-line to display the structure of an OLE file and its metadata, for example:

	OleFileIO_PL.py myfile.doc

You can use the option -c to check that all streams can be read fully, and -d to generate very verbose debugging information.

## Real-life examples ##

A real-life example: [using OleFileIO_PL for malware analysis and forensics](http://blog.gregback.net/2011/03/using-remnux-for-forensic-puzzle-6/).

See also [this paper](https://computer-forensics.sans.org/community/papers/gcfa/grow-forensic-tools-taxonomy-python-libraries-helpful-forensic-analysis_6879) about python tools for forensics, which features OleFileIO_PL.

About Python 2 and 3
--------------------

OleFileIO\_PL used to support only Python 2.x. As of version 0.30, the code has been changed to be compatible with Python 3.x. As a consequence, compatibility with Python 2.5 or older is not provided anymore. However, a copy of v0.26 is available as OleFileIO_PL2.py. See above the "import" section for a workaround.

If you think OleFileIO_PL should stay compatible with Python 2.5 or older, please [contact me](http://decalage.info/contact).

How to contribute
-----------------

The code is available in [a Mercurial repository on bitbucket](https://bitbucket.org/decalage/olefileio_pl). You may use it to submit enhancements or to report any issue.

If you would like to help us improve this module, or simply provide feedback, please [contact me](http://decalage.info/contact). You can help in many ways:

- test this module on different platforms / Python versions
- find and report bugs
- improve documentation, code samples, docstrings
- write unittest test cases
- provide tricky malformed files

How to report bugs
------------------

To report a bug, for example a normal file which is not parsed correctly, please use the [issue reporting page](https://bitbucket.org/decalage/olefileio_pl/issues?status=new&status=open), or if you prefer to do it privately, use this [contact form](http://decalage.info/contact). Please provide all the information about the context and how to reproduce the bug.

If possible please join the debugging output of OleFileIO_PL. For this, launch the following command :

	OleFileIO_PL.py -d -c file >debug.txt

License
-------

OleFileIO_PL is open-source.

OleFileIO_PL changes are Copyright (c) 2005-2014 by Philippe Lagadec.

The Python Imaging Library (PIL) is

- Copyright (c) 1997-2005 by Secret Labs AB

- Copyright (c) 1995-2005 by Fredrik Lundh

By obtaining, using, and/or copying this software and/or its associated documentation, you agree that you have read, understood, and will comply with the following terms and conditions:

Permission to use, copy, modify, and distribute this software and its associated documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appears in all copies, and that both that copyright notice and this permission notice appear in supporting documentation, and that the name of Secret Labs AB or the author not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
