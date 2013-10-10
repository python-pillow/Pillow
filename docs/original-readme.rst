Original PIL README
===================

What follows is the original PIL 1.1.7 README file contents.

::

    The Python Imaging Library
    $Id$

    Release 1.1.7 (November 15, 2009)

    ====================================================================
    The Python Imaging Library 1.1.7
    ====================================================================

    Contents
    --------

    + Introduction
    + Support Options
      - Commercial support
      - Free support
    + Software License
    + Build instructions (all platforms)
      - Additional notes for Mac OS X
      - Additional notes for Windows

    --------------------------------------------------------------------
    Introduction
    --------------------------------------------------------------------

    The Python Imaging Library (PIL) adds image processing capabilities
    to your Python environment.  This library provides extensive file
    format support, an efficient internal representation, and powerful
    image processing capabilities.

    This source kit has been built and tested with Python 2.0 and newer,
    on Windows, Mac OS X, and major Unix platforms.  Large parts of the
    library also work on 1.5.2 and 1.6.

    The main distribution site for this software is:

            http://www.pythonware.com/products/pil/

    That site also contains information about free and commercial support
    options, PIL add-ons, answers to frequently asked questions, and more.


    Development versions (alphas, betas) are available here:

            http://effbot.org/downloads/


    The PIL handbook is not included in this distribution; to get the
    latest version, check:

            http://www.pythonware.com/library/
            http://effbot.org/books/imagingbook/ (drafts)


    For installation and licensing details, see below.


    --------------------------------------------------------------------
    Support Options
    --------------------------------------------------------------------

    + Commercial Support

    Secret Labs (PythonWare) offers support contracts for companies using
    the Python Imaging Library in commercial applications, and in mission-
    critical environments.  The support contract includes technical support,
    bug fixes, extensions to the PIL library, sample applications, and more.

    For the full story, check:

            http://www.pythonware.com/products/pil/support.htm


    + Free Support

    For support and general questions on the Python Imaging Library, send
    e-mail to the Image SIG mailing list:

            image-sig@python.org

    You can join the Image SIG by sending a mail to:

            image-sig-request@python.org

    Put "subscribe" in the message body to automatically subscribe to the
    list, or "help" to get additional information.  Alternatively, you can
    send your questions to the Python mailing list, python-list@python.org,
    or post them to the newsgroup comp.lang.python.  DO NOT SEND SUPPORT
    QUESTIONS TO PYTHONWARE ADDRESSES.


    --------------------------------------------------------------------
    Software License
    --------------------------------------------------------------------

    The Python Imaging Library is

    Copyright (c) 1997-2009 by Secret Labs AB
    Copyright (c) 1995-2009 by Fredrik Lundh

    By obtaining, using, and/or copying this software and/or its
    associated documentation, you agree that you have read, understood,
    and will comply with the following terms and conditions:

    Permission to use, copy, modify, and distribute this software and its
    associated documentation for any purpose and without fee is hereby
    granted, provided that the above copyright notice appears in all
    copies, and that both that copyright notice and this permission notice
    appear in supporting documentation, and that the name of Secret Labs
    AB or the author not be used in advertising or publicity pertaining to
    distribution of the software without specific, written prior
    permission.

    SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO
    THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
    OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


    --------------------------------------------------------------------
    Build instructions (all platforms)
    --------------------------------------------------------------------

    For a list of changes in this release, see the CHANGES document.

    0. If you're in a hurry, try this:

            $ tar xvfz Imaging-1.1.7.tar.gz
            $ cd Imaging-1.1.7
            $ python setup.py install

       If you prefer to know what you're doing, read on.


    1. Prerequisites.

       If you need any of the features described below, make sure you
       have the necessary libraries before building PIL.

       feature              library
       -----------------------------------------------------------------
       JPEG support         libjpeg (6a or 6b)

                            http://www.ijg.org
                            http://www.ijg.org/files/jpegsrc.v6b.tar.gz
                            ftp://ftp.uu.net/graphics/jpeg/

       PNG support          zlib (1.2.3 or later is recommended)

                            http://www.gzip.org/zlib/

       OpenType/TrueType    freetype2 (2.3.9 or later is recommended)
       support
                            http://www.freetype.org
                            http://freetype.sourceforge.net

       CMS support          littleCMS (1.1.5 or later is recommended)
       support
                            http://www.littlecms.com/

       If you have a recent Linux version, the libraries provided with the
       operating system usually work just fine.  If some library is
       missing, installing a prebuilt version (jpeg-devel, zlib-devel,
       etc) is usually easier than building from source.  For example, for
       Ubuntu 9.10 (karmic), you can install the following libraries:

           sudo apt-get install libjpeg62-dev
           sudo apt-get install zlib1g-dev
           sudo apt-get install libfreetype6-dev
           sudo apt-get install liblcms1-dev

       If you're using Mac OS X, you can use the 'fink' tool to install
       missing libraries (also see the Mac OS X section below).

       Similar tools are available for many other platforms.


    2. To build under Python 1.5.2, you need to install the stand-alone
       version of the distutils library:

           http://www.python.org/sigs/distutils-sig/download.html

       You can fetch distutils 1.0.2 from the Python source repository:

           svn export http://svn.python.org/projects/python/tags/Distutils-1_0_2/Lib/distutils/

       For newer releases, the distutils library is included in the
       Python standard library.

       NOTE: Version 1.1.7 is not fully compatible with 1.5.2.  Some
       more recent additions to the library may not work, but the core
       functionality is available.


    3. If you didn't build Python from sources, make sure you have
       Python's build support files on your machine.  If you've down-
       loaded a prebuilt package (e.g. a Linux RPM), you probably
       need additional developer packages.  Look for packages named
       "python-dev", "python-devel", or similar.  For example, for
       Ubuntu 9.10 (karmic), use the following command:

           sudo apt-get install python-dev


    4. When you have everything you need, unpack the PIL distribution
       (the file Imaging-1.1.7.tar.gz) in a suitable work directory:

            $ cd MyExtensions # example
            $ gunzip Imaging-1.1.7.tar.gz
            $ tar xvf Imaging-1.1.7.tar


    5. Build the library.  We recommend that you do an in-place build,
       and run the self test before installing.

            $ cd Imaging-1.1.7
            $ python setup.py build_ext -i
            $ python selftest.py

       During the build process, the setup.py will display a summary
       report that lists what external components it found.  The self-
       test will display a similar report, with what external components
       the tests found in the actual build files:

            ----------------------------------------------------------------
            PIL 1.1.7 SETUP SUMMARY
            ----------------------------------------------------------------
            *** TKINTER support not available (Tcl/Tk 8.5 libraries needed)
            --- JPEG support available
            --- ZLIB (PNG/ZIP) support available
            --- FREETYPE support available
            ----------------------------------------------------------------

       Make sure that the optional components you need are included.

       If the build script won't find a given component, you can edit the
       setup.py file and set the appropriate ROOT variable.  For details,
       see instructions in the file.

       If the build script finds the component, but the tests cannot
       identify it, try rebuilding *all* modules:

            $ python setup.py clean
            $ python setup.py build_ext -i


    6. If the setup.py and selftest.py commands finish without any
       errors, you're ready to install the library:

            $ python setup.py install

       (depending on how Python has been installed on your machine,
       you might have to log in as a superuser to run the 'install'
       command, or use the 'sudo' command to run 'install'.)


    --------------------------------------------------------------------
    Additional notes for Mac OS X
    --------------------------------------------------------------------

    On Mac OS X you will usually install additional software such as
    libjpeg or freetype with the "fink" tool, and then it ends up in
    "/sw".  If you have installed the libraries elsewhere, you may have
    to tweak the "setup.py" file before building.


    --------------------------------------------------------------------
    Additional notes for Windows
    --------------------------------------------------------------------

    On Windows, you need to tweak the ROOT settings in the "setup.py"
    file, to make it find the external libraries.  See comments in the
    file for details.

    Make sure to build PIL and the external libraries with the same
    runtime linking options as was used for the Python interpreter
    (usually /MD, under Visual Studio).


    Note that most Python distributions for Windows include libraries
    compiled for Microsoft Visual Studio.  You can get the free Express
    edition of Visual Studio from:

        http://www.microsoft.com/Express/

    To build extensions using other tool chains, see the "Using
    non-Microsoft compilers on Windows" section in the distutils handbook:

        http://www.python.org/doc/current/inst/non-ms-compilers.html

    For additional information on how to build extensions using the
    popular MinGW compiler, see:

        http://mingw.org (compiler)
        http://sebsauvage.net/python/mingw.html (build instructions)
        http://sourceforge.net/projects/gnuwin32 (prebuilt libraries)
