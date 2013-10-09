Pillow
======

*Python Imaging Library (Fork)*

Pillow is the "friendly" PIL fork by Alex Clark and Contributors. PIL is the Python Imaging Library by Fredrik Lundh and Contributors.

.. image:: https://travis-ci.org/python-imaging/Pillow.png
   :target: https://travis-ci.org/python-imaging/Pillow

.. image:: https://pypip.in/v/Pillow/badge.png
    :target: https://pypi.python.org/pypi/Pillow/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Pillow/badge.png
    :target: https://pypi.python.org/pypi/Pillow/
    :alt: Number of PyPI downloads

The full documentation is hosted at http://pillow.readthedocs.org/. It
contains everything in this file plus tutorials, reference, compatibility
details, and more.

Introduction
------------

.. Note:: Pillow >= 2.1.0 no longer supports "import _imaging". Please use "from PIL.Image import core as _imaging" instead.

.. Note:: Pillow < 2.0.0 supports Python versions 2.4, 2.5, 2.6, 2.7; Pillow >= 2.0.0 supports Python versions 2.6, 2.7, 3.2, 3.3.

The fork author's goal is to foster active development of PIL through:

- Continuous integration testing via `Travis CI <https://travis-ci.org/python-imaging/Pillow>`_
- Publicized development activity on `GitHub <https://github.com/python-imaging/Pillow>`_
- Regular releases to the `Python Package Index <https://pypi.python.org/pypi/Pillow>`_
- Solicitation for community contributions and involvement on `Image-SIG <http://mail.python.org/mailman/listinfo/image-sig>`_

For information about why this fork exists and how it differs from PIL, see
`the About page in the documentation`_.

.. _the About page in the documentation: http://pillow.readthedocs.org/en/latest/about.html

Installation
------------

.. Note:: PIL and Pillow currently cannot co-exist in the same environment. If you want to use Pillow, please remove PIL first.

You can install Pillow with ``pip``::

    $ pip install Pillow

Or ``easy_install`` (for installing `Python Eggs <http://peak.telecommunity.com/DevCenter/PythonEggs>`_, as pip does not support them)::

    $ easy_install Pillow

Or download the compressed archive from PyPI, extract it, and inside it run::

    $ python setup.py install

For more information, please see http://pillow.readthedocs.org/en/latest/ or below.

Community Support
-----------------

Developer
~~~~~~~~~

PIL needs you! Please help us maintain the Python Imaging Library here:

- GitHub (https://github.com/python-imaging/Pillow)
- Freenode (irc://irc.freenode.net#pil)
- Image-SIG (http://mail.python.org/mailman/listinfo/image-sig)

Financial
~~~~~~~~~

Pillow is a volunteer effort led by Alex Clark. If you can't help with development, please help us financially; your assistance is very much needed and appreciated!

.. Note:: Contributors: please add your name and donation preference here. 

+--------------------------------------+---------------------------------------+
| **Developer**                        | **Preference**                        |
+--------------------------------------+---------------------------------------+
| Alex Clark (fork author)             | http://gittip.com/aclark4life         |
+--------------------------------------+---------------------------------------+

Developer Notes
---------------

.. Note:: If there is a binary package for your system, that is the easiest way to install Pillow. Currently we only provide binaries for Windows (via Python eggs).

Build from source
~~~~~~~~~~~~~~~~~

Many of Pillow's features require external libraries:

* **libjpeg** provides JPEG functionality.

  * Pillow has been tested with libjpeg versions **6b**, **8**, and **9**

* **zlib** provides access to compressed PNGs

* **libtiff** provides group4 tiff functionality

  * Pillow has been tested with libtiff versions **3.x** and **4.0**

* **libfreetype** provides type related services

* **littlecms** provides color management

* **libwebp** provides the Webp format.

  * Pillow has been tested with version **0.1.3**, which does not read transparent webp files. Version **0.3.0** supports transparency.

* **tcl/tk** provides support for tkinter bitmap and photo images. 

If the prerequisites are installed in the standard library locations for your machine (e.g. /usr or /usr/local), no additional configuration should be required. If they are installed in a non-standard location, you may need to configure setuptools to use those locations (i.e. by editing setup.py and/or setup.cfg). Once you have installed the prerequisites, run::

    $ pip install Pillow

Platform-specific instructions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Linux
+++++

**We do not provide binaries for Linux.** If you didn't build Python from source, make sure you have Python's development libraries installed. In Debian or Ubuntu::

    $ sudo apt-get install python-dev python-setuptools

Or for Python 3::

    $ sudo apt-get install python3-dev python3-setuptools

Prerequisites are installed on **Ubuntu 10.04 LTS** with::

    $ sudo apt-get install libtiff4-dev libjpeg62-dev zlib1g-dev libfreetype6-dev liblcms1-dev tcl8.5-dev tk8.5-dev

Prerequisites are installed with on **Ubuntu 12.04 LTS** or **Raspian Wheezy 7.0** with::

    $ sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms1-dev libwebp-dev tcl8.5-dev tk8.5-dev

Distributions
^^^^^^^^^^^^^

.. Note:: XXX Provide links

Additionally, many Linux distributions now include Pillow (instead of PIL) with their distribution:

- Fedora
- Debian/Ubuntu
- ArchLinux

Mac OS X
++++++++

**We do not provide binaries for OS X.** So you'll need XCode to install Pillow. (XCode 4.2 on 10.6 will work with the Official Python binary distribution. Otherwise, use whatever XCode you used to compile Python.)

The easiest way to install the prerequisites is via `Homebrew <http://mxcl.github.com/homebrew/>`_. After you install Homebrew, run::

    $ brew install libtiff libjpeg webp littlecms

If you've built your own Python, then you should be able to install Pillow using::

    $ pip install Pillow

Windows
+++++++

We provide binaries for Windows in the form of Python Eggs and `Python Wheels <http://wheel.readthedocs.org/en/latest/index.html>`_:

Python Eggs
^^^^^^^^^^^

.. Note:: Pip does not support Python Eggs; use easy_install instead.

::

    $ easy_install Pillow

Python Wheels
^^^^^^^^^^^^^

.. Note:: Experimental. Requires Setuptools >=0.8 and Pip >=1.4.1

::

    $ pip install --use-wheel Pillow

Platform support
~~~~~~~~~~~~~~~~

Current platform support for Pillow is documented here:
http://pillow.readthedocs.org/en/latest/installation.html#platform-support

Port existing PIL-based code to Pillow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pillow is a functional drop-in replacement for the Python Imaging Library. To run your existing PIL-compatible code with Pillow, it needs to be modified to import the ``Imaging`` module from the ``PIL`` namespace *instead* of the global namespace. I.e. change::

    import Image

to::

    from PIL import Image

.. Note:: If your code imports from ``_imaging``, it will no longer work.

The preferred, future proof method of importing the private ``_imaging`` module is::

    from PIL import Image
    _imaging = Image.core
