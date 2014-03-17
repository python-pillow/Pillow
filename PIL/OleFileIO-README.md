OleFileIO_PL
============

[OleFileIO_PL](http://www.decalage.info/python/olefileio) is a Python module to read [Microsoft OLE2 files (also called Structured Storage, Compound File Binary Format or Compound Document File Format)](http://en.wikipedia.org/wiki/Compound_File_Binary_Format), such as Microsoft Office documents, Image Composer and FlashPix files, Outlook messages, ... 

This is an improved version of the OleFileIO module from [PIL](http://www.pythonware.com/products/pil/index.htm), the excellent Python Imaging Library, created and maintained by Fredrik Lundh. The API is still compatible with PIL, but I have improved the internal implementation significantly, with new features, bugfixes and a more robust design.

As far as I know, this module is now the most complete and robust Python implementation to read MS OLE2 files, portable on several operating systems. (please tell me if you know other similar Python modules)

WARNING: THIS IS (STILL) WORK IN PROGRESS.

Main improvements over PIL version of OleFileIO:
------------------------------------------------

- Better compatibility with Python 2.6 (also compatible with Python 3.0+)
- Support for files larger than 6.8MB
- Robust: many checks to detect malformed files
- Improved API
- New features: metadata extraction, stream/storage timestamps
- Added setup.py and install.bat to ease installation

News
----

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

Download:
---------

The archive is available on [the project page](https://bitbucket.org/decalage/olefileio_pl/downloads).


How to use this module:
-----------------------

See sample code at the end of the module, and also docstrings.

Here are a few examples:

	:::python
		import OleFileIO_PL
		
		# Test if a file is an OLE container:
		assert OleFileIO_PL.isOleFile('myfile.doc')
		
		# Open an OLE file from disk:
		ole = OleFileIO_PL.OleFileIO('myfile.doc')
		
		# Get list of streams:
		print(ole.listdir())
		
		# Test if known streams/storages exist:
		if ole.exists('worddocument'):
		    print("This is a Word document.")
		    print("size :", ole.get_size('worddocument'))
		    if ole.exists('macros/vba'):
		         print("This document seems to contain VBA macros.")

		# Extract the "Pictures" stream from a PPT file:
		if ole.exists('Pictures'):
		    pics = ole.openstream('Pictures')
		    data = pics.read()
		    f = open('Pictures.bin', 'wb')
		    f.write(data)
		    f.close()

		# Extract metadata (new in v0.24) - see source code for all attributes:
		meta = ole.get_metadata()
		print('Author:', meta.author)
		print('Title:', meta.title)
		print('Creation date:', meta.create_time)
		# print all metadata:
		meta.dump()

		# Close the OLE file:
		ole.close()
		
		# Work with a file-like object (e.g. StringIO) instead of a file on disk:
		data = open('myfile.doc', 'rb').read()
		f = io.BytesIO(data)
		ole = OleFileIO_PL.OleFileIO(f)
		print(ole.listdir())
		ole.close()
		
		
It can also be used as a script from the command-line to display the structure of an OLE file, for example:

	OleFileIO_PL.py myfile.doc

A real-life example: [using OleFileIO_PL for malware analysis and forensics](http://blog.gregback.net/2011/03/using-remnux-for-forensic-puzzle-6/).

How to contribute:
------------------

The code is available in [a Mercurial repository on bitbucket](https://bitbucket.org/decalage/olefileio_pl). You may use it to submit enhancements or to report any issue.

If you would like to help us improve this module, or simply provide feedback, you may also send an e-mail to decalage(at)laposte.net. You can help in many ways:

- test this module on different platforms / Python versions
- find and report bugs
- improve documentation, code samples, docstrings
- write unittest test cases
- provide tricky malformed files

How to report bugs:
-------------------

To report a bug, for example a normal file which is not parsed correctly, please use the [issue reporting page](https://bitbucket.org/decalage/olefileio_pl/issues?status=new&status=open), or send an e-mail with an attachment containing the debugging output of OleFileIO_PL.

For this, launch the following command :

	OleFileIO_PL.py -d -c file >debug.txt 

License
-------

OleFileIO_PL is open-source.

OleFileIO_PL changes are Copyright (c) 2005-2013 by Philippe Lagadec.

The Python Imaging Library (PIL) is

- Copyright (c) 1997-2005 by Secret Labs AB

- Copyright (c) 1995-2005 by Fredrik Lundh

By obtaining, using, and/or copying this software and/or its associated documentation, you agree that you have read, understood, and will comply with the following terms and conditions:

Permission to use, copy, modify, and distribute this software and its associated documentation for any purpose and without fee is hereby granted, provided that the above copyright notice appears in all copies, and that both that copyright notice and this permission notice appear in supporting documentation, and that the name of Secret Labs AB or the author not be used in advertising or publicity pertaining to distribution of the software without specific, written prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
