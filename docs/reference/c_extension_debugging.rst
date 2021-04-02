C Extension debugging on Linux, with gbd/valgrind.
==================================================

Install the tools
-----------------

You need some basics in addition to the basic tools to build
pillow. These are what's required on Ubuntu, YMMV for other
distributions.

-  ``python3-dbg`` package for the gdb extensions and python symbols
-  ``gdb`` and ``valgrind``
-  Potentially debug symbols for libraries. On ubuntu they're shipped
   in package-dbgsym packages, from a different repo.

::

    deb http://ddebs.ubuntu.com focal main restricted universe multiverse
    deb http://ddebs.ubuntu.com focal-updates main restricted universe multiverse
    deb http://ddebs.ubuntu.com focal-proposed main restricted universe multiverse

Then ``sudo apt-get update && sudo apt-get install libtiff5-dbgsym``

-  There's a bug with the dbg package for at least python 3.8 on ubuntu
   20.04, and you need to add a new link or two to make it autoload when
   running python:

::

    cd /usr/share/gdb/auto-load/usr/bin
    ln -s python3.8m-gdb.py python3.8d-gdb.py

-  In Ubuntu 18.04, it's actually including the path to the virtualenv
   in the search for the ``python3.*-gdb.py`` file, but you can
   helpfully put in the same directory as the binary.

-  I also find that history is really useful for gdb, so I added this to
   my ``~/.gdbinit`` file:

::

    set history filename ~/.gdb_history
    set history save on

-  If the python stack isn't working in gdb, then
   ``set debug auto-load`` can also be helpful in ``.gdbinit``.

-  Make a virtualenv with the debug python and activate it, then install
   whatever dependencies are required and build. You want to build with
   the debug python so you get symbols for your extension.

::

    virtualenv -p python3.8-dbg ~/vpy38-dbg
    source ~/vpy38-dbg/bin/activate
    cd ~/Pillow && pip install -r requirements.txt && make install

Test Case
---------

Take your test image, and make a really simple harness.

::

    from PIL import Image
    with Image.open(path) as im:
        im.load()

-  Run this through valgrind, but note that python triggers some issues
   on its own, so you're looking for items within the Pillow hierarchy
   that don't look like they're solely in the python call chain. In this
   example, the ones we're interested are after the warnings, and have
   ``decode.c`` and ``TiffDecode.c`` in the call stack:

::

    (vpy38-dbg) ubuntu@primary:~/Home/tests$ valgrind python test_tiff.py
    ==51890== Memcheck, a memory error detector
    ==51890== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
    ==51890== Using Valgrind-3.15.0 and LibVEX; rerun with -h for copyright info
    ==51890== Command: python test_tiff.py
    ==51890==
    ==51890== Invalid read of size 4
    ==51890==    at 0x472E3D: address_in_range (obmalloc.c:1401)
    ==51890==    by 0x472EEA: pymalloc_free (obmalloc.c:1677)
    ==51890==    by 0x474960: _PyObject_Free (obmalloc.c:1896)
    ==51890==    by 0x473BAC: _PyMem_DebugRawFree (obmalloc.c:2187)
    ==51890==    by 0x473BD4: _PyMem_DebugFree (obmalloc.c:2318)
    ==51890==    by 0x474C08: PyObject_Free (obmalloc.c:709)
    ==51890==    by 0x45DD60: dictresize (dictobject.c:1259)
    ==51890==    by 0x45DD76: insertion_resize (dictobject.c:1019)
    ==51890==    by 0x464F30: PyDict_SetDefault (dictobject.c:2924)
    ==51890==    by 0x4D03BE: PyUnicode_InternInPlace (unicodeobject.c:15289)
    ==51890==    by 0x4D0700: PyUnicode_InternFromString (unicodeobject.c:15322)
    ==51890==    by 0x64D2FC: descr_new (descrobject.c:857)
    ==51890==  Address 0x4c1b020 is 384 bytes inside a block of size 1,160 free'd
    ==51890==    at 0x483CA3F: free (in /usr/lib/x86_64-linux-gnu/valgrind/vgpreload_memcheck-amd64-linux.so)
    ==51890==    by 0x4735D3: _PyMem_RawFree (obmalloc.c:127)
    ==51890==    by 0x473BAC: _PyMem_DebugRawFree (obmalloc.c:2187)
    ==51890==    by 0x474941: PyMem_RawFree (obmalloc.c:595)
    ==51890==    by 0x47496E: _PyObject_Free (obmalloc.c:1898)
    ==51890==    by 0x473BAC: _PyMem_DebugRawFree (obmalloc.c:2187)
    ==51890==    by 0x473BD4: _PyMem_DebugFree (obmalloc.c:2318)
    ==51890==    by 0x474C08: PyObject_Free (obmalloc.c:709)
    ==51890==    by 0x45DD60: dictresize (dictobject.c:1259)
    ==51890==    by 0x45DD76: insertion_resize (dictobject.c:1019)
    ==51890==    by 0x464F30: PyDict_SetDefault (dictobject.c:2924)
    ==51890==    by 0x4D03BE: PyUnicode_InternInPlace (unicodeobject.c:15289)
    ==51890==  Block was alloc'd at
    ==51890==    at 0x483B7F3: malloc (in /usr/lib/x86_64-linux-gnu/valgrind/vgpreload_memcheck-amd64-linux.so)
    ==51890==    by 0x473646: _PyMem_RawMalloc (obmalloc.c:99)
    ==51890==    by 0x473529: _PyMem_DebugRawAlloc (obmalloc.c:2120)
    ==51890==    by 0x473565: _PyMem_DebugRawMalloc (obmalloc.c:2153)
    ==51890==    by 0x4748B1: PyMem_RawMalloc (obmalloc.c:572)
    ==51890==    by 0x475909: _PyObject_Malloc (obmalloc.c:1628)
    ==51890==    by 0x473529: _PyMem_DebugRawAlloc (obmalloc.c:2120)
    ==51890==    by 0x473565: _PyMem_DebugRawMalloc (obmalloc.c:2153)
    ==51890==    by 0x4736B0: _PyMem_DebugMalloc (obmalloc.c:2303)
    ==51890==    by 0x474B78: PyObject_Malloc (obmalloc.c:685)
    ==51890==    by 0x45C435: new_keys_object (dictobject.c:558)
    ==51890==    by 0x45DA95: dictresize (dictobject.c:1202)
    ==51890==
    ==51890== Invalid read of size 4
    ==51890==    at 0x472E3D: address_in_range (obmalloc.c:1401)
    ==51890==    by 0x47594A: pymalloc_realloc (obmalloc.c:1929)
    ==51890==    by 0x475A02: _PyObject_Realloc (obmalloc.c:1982)
    ==51890==    by 0x473DCA: _PyMem_DebugRawRealloc (obmalloc.c:2240)
    ==51890==    by 0x473FF8: _PyMem_DebugRealloc (obmalloc.c:2326)
    ==51890==    by 0x4749FB: PyMem_Realloc (obmalloc.c:623)
    ==51890==    by 0x44A6FC: list_resize (listobject.c:70)
    ==51890==    by 0x44A872: app1 (listobject.c:340)
    ==51890==    by 0x44FD65: PyList_Append (listobject.c:352)
    ==51890==    by 0x514315: r_ref (marshal.c:945)
    ==51890==    by 0x516034: r_object (marshal.c:1139)
    ==51890==    by 0x516C70: r_object (marshal.c:1389)
    ==51890==  Address 0x4c41020 is 32 bytes before a block of size 1,600 in arena "client"
    ==51890==
    ==51890== Conditional jump or move depends on uninitialised value(s)
    ==51890==    at 0x472E46: address_in_range (obmalloc.c:1403)
    ==51890==    by 0x47594A: pymalloc_realloc (obmalloc.c:1929)
    ==51890==    by 0x475A02: _PyObject_Realloc (obmalloc.c:1982)
    ==51890==    by 0x473DCA: _PyMem_DebugRawRealloc (obmalloc.c:2240)
    ==51890==    by 0x473FF8: _PyMem_DebugRealloc (obmalloc.c:2326)
    ==51890==    by 0x4749FB: PyMem_Realloc (obmalloc.c:623)
    ==51890==    by 0x44A6FC: list_resize (listobject.c:70)
    ==51890==    by 0x44A872: app1 (listobject.c:340)
    ==51890==    by 0x44FD65: PyList_Append (listobject.c:352)
    ==51890==    by 0x5E3321: _posix_listdir (posixmodule.c:3823)
    ==51890==    by 0x5E33A8: os_listdir_impl (posixmodule.c:3879)
    ==51890==    by 0x5E4D77: os_listdir (posixmodule.c.h:1197)
    ==51890==
    ==51890== Use of uninitialised value of size 8
    ==51890==    at 0x472E59: address_in_range (obmalloc.c:1403)
    ==51890==    by 0x47594A: pymalloc_realloc (obmalloc.c:1929)
    ==51890==    by 0x475A02: _PyObject_Realloc (obmalloc.c:1982)
    ==51890==    by 0x473DCA: _PyMem_DebugRawRealloc (obmalloc.c:2240)
    ==51890==    by 0x473FF8: _PyMem_DebugRealloc (obmalloc.c:2326)
    ==51890==    by 0x4749FB: PyMem_Realloc (obmalloc.c:623)
    ==51890==    by 0x44A6FC: list_resize (listobject.c:70)
    ==51890==    by 0x44A872: app1 (listobject.c:340)
    ==51890==    by 0x44FD65: PyList_Append (listobject.c:352)
    ==51890==    by 0x5E3321: _posix_listdir (posixmodule.c:3823)
    ==51890==    by 0x5E33A8: os_listdir_impl (posixmodule.c:3879)
    ==51890==    by 0x5E4D77: os_listdir (posixmodule.c.h:1197)
    ==51890==
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 16908288 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 67895296 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 1572864 bytes but only got 0. Skipping tag 42
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 116647 bytes but only got 4867. Skipping tag 42738
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 3468830728 bytes but only got 4851. Skipping tag 279
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 2198732800 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 67239937 bytes but only got 4125. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33947764 bytes but only got 0. Skipping tag 139
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 17170432 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 80478208 bytes but only got 0. Skipping tag 1
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 787460 bytes but only got 4882. Skipping tag 20
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 1075 bytes but only got 0. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 120586240 bytes but only got 0. Skipping tag 194
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 65536 bytes but only got 0. Skipping tag 3
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 198656 bytes but only got 0. Skipping tag 279
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 206848 bytes but only got 0. Skipping tag 64512
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 130968 bytes but only got 4882. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 77848 bytes but only got 4689. Skipping tag 64270
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 262156 bytes but only got 0. Skipping tag 257
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33624064 bytes but only got 0. Skipping tag 49152
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 67178752 bytes but only got 4627. Skipping tag 50688
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33632768 bytes but only got 0. Skipping tag 56320
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 134386688 bytes but only got 4115. Skipping tag 2048
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33912832 bytes but only got 0. Skipping tag 7168
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 151966208 bytes but only got 4627. Skipping tag 10240
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 119032832 bytes but only got 3859. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 46535680 bytes but only got 0. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 35651584 bytes but only got 0. Skipping tag 42
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 524288 bytes but only got 0. Skipping tag 0
      warnings.warn(
    _TIFFVSetField: tempfile.tif: Null count for "Tag 769" (type 1, writecount -3, passcount 1).
    _TIFFVSetField: tempfile.tif: Null count for "Tag 42754" (type 1, writecount -3, passcount 1).
    _TIFFVSetField: tempfile.tif: Null count for "Tag 769" (type 1, writecount -3, passcount 1).
    _TIFFVSetField: tempfile.tif: Null count for "Tag 42754" (type 1, writecount -3, passcount 1).
    ZIPDecode: Decoding error at scanline 0, incorrect header check.
    ==51890== Invalid write of size 4
    ==51890==    at 0x61C39E6: putcontig8bitYCbCr22tile (tif_getimage.c:2146)
    ==51890==    by 0x61C5865: gtStripContig (tif_getimage.c:977)
    ==51890==    by 0x6094317: ReadStrip (TiffDecode.c:269)
    ==51890==    by 0x6094749: ImagingLibTiffDecode (TiffDecode.c:479)
    ==51890==    by 0x60615D1: _decode (decode.c:136)
    ==51890==    by 0x64BF47: method_vectorcall_VARARGS (descrobject.c:300)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==    by 0x43627B: function_code_fastcall (call.c:283)
    ==51890==    by 0x436D21: _PyFunction_Vectorcall (call.c:410)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==  Address 0x6f456d4 is 0 bytes after a block of size 68 alloc'd
    ==51890==    at 0x483DFAF: realloc (in /usr/lib/x86_64-linux-gnu/valgrind/vgpreload_memcheck-amd64-linux.so)
    ==51890==    by 0x60946D0: ImagingLibTiffDecode (TiffDecode.c:469)
    ==51890==    by 0x60615D1: _decode (decode.c:136)
    ==51890==    by 0x64BF47: method_vectorcall_VARARGS (descrobject.c:300)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==    by 0x43627B: function_code_fastcall (call.c:283)
    ==51890==    by 0x436D21: _PyFunction_Vectorcall (call.c:410)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==    by 0x4DFDFB: _PyEval_EvalCodeWithName (ceval.c:4298)
    ==51890==    by 0x436C40: _PyFunction_Vectorcall (call.c:435)
    ==51890==
    ==51890== Invalid write of size 4
    ==51890==    at 0x61C39B5: putcontig8bitYCbCr22tile (tif_getimage.c:2145)
    ==51890==    by 0x61C5865: gtStripContig (tif_getimage.c:977)
    ==51890==    by 0x6094317: ReadStrip (TiffDecode.c:269)
    ==51890==    by 0x6094749: ImagingLibTiffDecode (TiffDecode.c:479)
    ==51890==    by 0x60615D1: _decode (decode.c:136)
    ==51890==    by 0x64BF47: method_vectorcall_VARARGS (descrobject.c:300)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==    by 0x43627B: function_code_fastcall (call.c:283)
    ==51890==    by 0x436D21: _PyFunction_Vectorcall (call.c:410)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==  Address 0x6f456d8 is 4 bytes after a block of size 68 alloc'd
    ==51890==    at 0x483DFAF: realloc (in /usr/lib/x86_64-linux-gnu/valgrind/vgpreload_memcheck-amd64-linux.so)
    ==51890==    by 0x60946D0: ImagingLibTiffDecode (TiffDecode.c:469)
    ==51890==    by 0x60615D1: _decode (decode.c:136)
    ==51890==    by 0x64BF47: method_vectorcall_VARARGS (descrobject.c:300)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==    by 0x43627B: function_code_fastcall (call.c:283)
    ==51890==    by 0x436D21: _PyFunction_Vectorcall (call.c:410)
    ==51890==    by 0x4EB73C: _PyObject_Vectorcall (abstract.h:127)
    ==51890==    by 0x4EB73C: call_function (ceval.c:4963)
    ==51890==    by 0x4EB73C: _PyEval_EvalFrameDefault (ceval.c:3486)
    ==51890==    by 0x4DF2EE: PyEval_EvalFrameEx (ceval.c:741)
    ==51890==    by 0x4DFDFB: _PyEval_EvalCodeWithName (ceval.c:4298)
    ==51890==    by 0x436C40: _PyFunction_Vectorcall (call.c:435)
    ==51890==
    TIFFFillStrip: Invalid strip byte count 0, strip 1.
    Traceback (most recent call last):
      File "test_tiff.py", line 8, in <module>
        im.load()
      File "/home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py", line 1087, in load
        return self._load_libtiff()
      File "/home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py", line 1191, in _load_libtiff
        raise OSError(err)
    OSError: -2
    sys:1: ResourceWarning: unclosed file <_io.BufferedReader name='crash-2020-10-test.tiff'>
    ==51890==
    ==51890== HEAP SUMMARY:
    ==51890==     in use at exit: 748,734 bytes in 444 blocks
    ==51890==   total heap usage: 6,320 allocs, 5,876 frees, 69,142,969 bytes allocated
    ==51890==
    ==51890== LEAK SUMMARY:
    ==51890==    definitely lost: 0 bytes in 0 blocks
    ==51890==    indirectly lost: 0 bytes in 0 blocks
    ==51890==      possibly lost: 721,538 bytes in 372 blocks
    ==51890==    still reachable: 27,196 bytes in 72 blocks
    ==51890==         suppressed: 0 bytes in 0 blocks
    ==51890== Rerun with --leak-check=full to see details of leaked memory
    ==51890==
    ==51890== Use --track-origins=yes to see where uninitialised values come from
    ==51890== For lists of detected and suppressed errors, rerun with: -s
    ==51890== ERROR SUMMARY: 2556 errors from 6 contexts (suppressed: 0 from 0)
    (vpy38-dbg) ubuntu@primary:~/Home/tests$

-  Now that we've confirmed that there's something odd/bad going on,
   it's time to gdb.
-  Start with ``gdb python``
-  Set a break point starting with the valgrind stack trace.
   ``b TiffDecode.c:269``
-  Run the script with ``r test_tiff.py``
-  When the break point is hit, explore the state with ``info locals``,
   ``bt``, ``py-bt``, or ``p [variable]``. For pointers,
   ``p *[variable]`` is useful.

::

    (vpy38-dbg) ubuntu@primary:~/Home/tests$ gdb python
    GNU gdb (Ubuntu 9.2-0ubuntu1~20.04) 9.2
    Copyright (C) 2020 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.
    Type "show copying" and "show warranty" for details.
    This GDB was configured as "x86_64-linux-gnu".
    Type "show configuration" for configuration details.
    For bug reporting instructions, please see:
    <http://www.gnu.org/software/gdb/bugs/>.
    Find the GDB manual and other documentation resources online at:
        <http://www.gnu.org/software/gdb/documentation/>.

    For help, type "help".
    Type "apropos word" to search for commands related to "word"...
    Reading symbols from python...
    (gdb) b TiffDecode.c:269
    No source file named TiffDecode.c.
    Make breakpoint pending on future shared library load? (y or [n]) y
    Breakpoint 1 (TiffDecode.c:269) pending.
    (gdb) r test_tiff.py
    Starting program: /home/ubuntu/vpy38-dbg/bin/python test_tiff.py
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 16908288 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 67895296 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 1572864 bytes but only got 0. Skipping tag 42
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 116647 bytes but only got 4867. Skipping tag 42738
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 3468830728 bytes but only got 4851. Skipping tag 279
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 2198732800 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 67239937 bytes but only got 4125. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33947764 bytes but only got 0. Skipping tag 139
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 17170432 bytes but only got 0. Skipping tag 0
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 80478208 bytes but only got 0. Skipping tag 1
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 787460 bytes but only got 4882. Skipping tag 20
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 1075 bytes but only got 0. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 120586240 bytes but only got 0. Skipping tag 194
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 65536 bytes but only got 0. Skipping tag 3
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 198656 bytes but only got 0. Skipping tag 279
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 206848 bytes but only got 0. Skipping tag 64512
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 130968 bytes but only got 4882. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 77848 bytes but only got 4689. Skipping tag 64270
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 262156 bytes but only got 0. Skipping tag 257
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33624064 bytes but only got 0. Skipping tag 49152
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 67178752 bytes but only got 4627. Skipping tag 50688
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33632768 bytes but only got 0. Skipping tag 56320
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 134386688 bytes but only got 4115. Skipping tag 2048
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 33912832 bytes but only got 0. Skipping tag 7168
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 151966208 bytes but only got 4627. Skipping tag 10240
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 119032832 bytes but only got 3859. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 46535680 bytes but only got 0. Skipping tag 256
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 35651584 bytes but only got 0. Skipping tag 42
      warnings.warn(
    /home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py:770: UserWarning: Possibly corrupt EXIF data.  Expecting to read 524288 bytes but only got 0. Skipping tag 0
      warnings.warn(
    _TIFFVSetField: tempfile.tif: Null count for "Tag 769" (type 1, writecount -3, passcount 1).
    _TIFFVSetField: tempfile.tif: Null count for "Tag 42754" (type 1, writecount -3, passcount 1).
    _TIFFVSetField: tempfile.tif: Null count for "Tag 769" (type 1, writecount -3, passcount 1).
    _TIFFVSetField: tempfile.tif: Null count for "Tag 42754" (type 1, writecount -3, passcount 1).

    Breakpoint 1, ReadStrip (tiff=tiff@entry=0xae9b90, row=0, buffer=0xac2eb0) at src/libImaging/TiffDecode.c:269
    269                 ok = TIFFRGBAImageGet(&img, buffer, img.width, rows_to_read);
    (gdb) p img
    $1 = {tif = 0xae9b90, stoponerr = 0, isContig = 1, alpha = 0, width = 20, height = 1536, bitspersample = 8, samplesperpixel = 3,
      orientation = 1, req_orientation = 1, photometric = 6, redcmap = 0x0, greencmap = 0x0, bluecmap = 0x0, get =
        0x7ffff71d0710 <gtStripContig>, put = {any = 0x7ffff71ce550 <putcontig8bitYCbCr22tile>,
        contig = 0x7ffff71ce550 <putcontig8bitYCbCr22tile>, separate = 0x7ffff71ce550 <putcontig8bitYCbCr22tile>}, Map = 0x0,
      BWmap = 0x0, PALmap = 0x0, ycbcr = 0xaf24b0, cielab = 0x0, UaToAa = 0x0, Bitdepth16To8 = 0x0, row_offset = 0, col_offset = 0}
    (gdb) up
    #1  0x00007ffff736174a in ImagingLibTiffDecode (im=0xac1f90, state=0x7ffff76767e0, buffer=<optimized out>, bytes=<optimized out>)
        at src/libImaging/TiffDecode.c:479
    479                 if (ReadStrip(tiff, state->y, (UINT32 *)state->buffer) == -1) {
    (gdb) p *state
    $2 = {count = 0, state = 0, errcode = 0, x = 0, y = 0, ystep = 0, xsize = 17, ysize = 108, xoff = 0, yoff = 0,
      shuffle = 0x7ffff735f411 <copy4>, bits = 32, bytes = 68, buffer = 0xac2eb0 "P\354\336\367\377\177", context = 0xa75440, fd = 0x0}
    (gdb) py-bt
    Traceback (most recent call first):
      File "/home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py", line 1428, in _load_libtiff

      File "/home/ubuntu/vpy38-dbg/lib/python3.8/site-packages/Pillow-8.0.1-py3.8-linux-x86_64.egg/PIL/TiffImagePlugin.py", line 1087, in load
        return self._load_libtiff()
      File "test_tiff.py", line 8, in <module>
        im.load()

-  Poke around till you understand what's going on. In this case,
   state->xsize and img.width are different, which led to an out of
   bounds write, as the receiving buffer was sized for the smaller of
   the two.

Caveats
-------

-  If your program is running/hung in a docker container and your host
   has the appropriate tools, you can run gdb as the superuser in the
   host and you may be able to get a trace of where the process is hung.
   You probably won't have the capability to do that from within the
   docker container, as the trace capacity isn't allowed by default.

-  Variations of this are possible on the mac/windows, but the details
   are going to be different.

-  IIRC, Fedora has the gdb bits working by default. Ubuntu has always
   been a bit of a battle to make it work.
