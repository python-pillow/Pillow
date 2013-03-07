
Pillow
======

.. image:: https://travis-ci.org/python-imaging/Pillow.png

Pillow is the "friendly" PIL fork by Alex Clark and Contributors. PIL is the Python Imaging Library by Fredrik Lundh and Contributors.

Introduction
------------

The fork author's goal is to foster active development of PIL through:

- Continuous integration testing via Travis-CI
- Publicized development activity on GitHub
- Regular releases to the Python Packaging Index
- Solicitation for community contributions and involvement on Imaging-SIG

Why a fork?
-----------

PIL is not setuptools compatible. Please see http://mail.python.org/pipermail/image-sig/2010-August/006480.html for a more detailed explanation. Also, PIL's current bi-yearly (or greater) release schedule is too infrequent to accomodate the large number and frequency of issues reported.

What about image code bugs?
---------------------------

Please report any non-packaging related issues here first:

- https://bitbucket.org/effbot/pil-2009-raclette/issues 

Then open a ticket here:

- https://github.com/python-imaging/Pillow/issues

and provide a link to the first ticket so we can track the issue(s) upstream. Prior to Pillow 2.0.0, very few (if any) image code changes were made. Pillow 2.0.0 and later includes Python 3 support and many bug fixes gathered from across the internet.

Documentation
-------------

The API documentation included with PIL has been converted (from HTML) to
reStructured text (via pandoc) and is now `hosted by readthedocs.org <http://pillow.readthedocs.org>`_.

What follows is the original PIL 1.1.7 README contents.

Python Imaging Library
======================

Introduction
------------

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

For installation and licensing details, see below.

--------------------------------------------------------------------
Support Options
--------------------------------------------------------------------

Commercial Support
~~~~~~~~~~~~~~~~~~

Secret Labs (PythonWare) offers support contracts for companies using
the Python Imaging Library in commercial applications, and in mission-
critical environments.  The support contract includes technical support,
bug fixes, extensions to the PIL library, sample applications, and more.

For the full story, check:

        http://www.pythonware.com/products/pil/support.htm


Free Support
~~~~~~~~~~~~

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

See COPYING
