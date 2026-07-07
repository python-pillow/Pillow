10.3.0
------

Security
========

ImageMath eval()
^^^^^^^^^^^^^^^^

.. danger::
  ``ImageMath.eval()`` uses Python's ``eval()`` function to process the expression
  string, and carries the security risks of doing so. A direct replacement for this is
  the new :py:meth:`~PIL.ImageMath.unsafe_eval`, but that carries the same risks. It is
  not recommended to process expressions without considering this.
  :py:meth:`~PIL.ImageMath.lambda_eval` is a more secure alternative.

:cve:`2024-28219`: Fix buffer overflow in ``_imagingcms.c``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In ``_imagingcms.c``, two ``strcpy`` calls were able to copy too much data into fixed
length strings. This has been fixed by using ``strncpy`` instead.

Deprecations
============

ImageCms constants and versions() function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A number of constants and a function in :py:mod:`.ImageCms` have been deprecated.
This includes a table of flags based on LittleCMS version 1 which has been replaced
with a new class :py:class:`.ImageCms.Flags` based on LittleCMS 2 flags.

============================================  ====================================================
Deprecated                                    Use instead
============================================  ====================================================
``ImageCms.DESCRIPTION``                      No replacement
``ImageCms.VERSION``                          ``PIL.__version__``
``ImageCms.FLAGS["MATRIXINPUT"]``             :py:attr:`.ImageCms.Flags.CLUT_POST_LINEARIZATION`
``ImageCms.FLAGS["MATRIXOUTPUT"]``            :py:attr:`.ImageCms.Flags.FORCE_CLUT`
``ImageCms.FLAGS["MATRIXONLY"]``              No replacement
``ImageCms.FLAGS["NOWHITEONWHITEFIXUP"]``     :py:attr:`.ImageCms.Flags.NOWHITEONWHITEFIXUP`
``ImageCms.FLAGS["NOPRELINEARIZATION"]``      :py:attr:`.ImageCms.Flags.CLUT_PRE_LINEARIZATION`
``ImageCms.FLAGS["GUESSDEVICECLASS"]``        :py:attr:`.ImageCms.Flags.GUESSDEVICECLASS`
``ImageCms.FLAGS["NOTCACHE"]``                :py:attr:`.ImageCms.Flags.NOCACHE`
``ImageCms.FLAGS["NOTPRECALC"]``              :py:attr:`.ImageCms.Flags.NOOPTIMIZE`
``ImageCms.FLAGS["NULLTRANSFORM"]``           :py:attr:`.ImageCms.Flags.NULLTRANSFORM`
``ImageCms.FLAGS["HIGHRESPRECALC"]``          :py:attr:`.ImageCms.Flags.HIGHRESPRECALC`
``ImageCms.FLAGS["LOWRESPRECALC"]``           :py:attr:`.ImageCms.Flags.LOWRESPRECALC`
``ImageCms.FLAGS["GAMUTCHECK"]``              :py:attr:`.ImageCms.Flags.GAMUTCHECK`
``ImageCms.FLAGS["WHITEBLACKCOMPENSATION"]``  :py:attr:`.ImageCms.Flags.BLACKPOINTCOMPENSATION`
``ImageCms.FLAGS["BLACKPOINTCOMPENSATION"]``  :py:attr:`.ImageCms.Flags.BLACKPOINTCOMPENSATION`
``ImageCms.FLAGS["SOFTPROOFING"]``            :py:attr:`.ImageCms.Flags.SOFTPROOFING`
``ImageCms.FLAGS["PRESERVEBLACK"]``           :py:attr:`.ImageCms.Flags.NONEGATIVES`
``ImageCms.FLAGS["NODEFAULTRESOURCEDEF"]``    :py:attr:`.ImageCms.Flags.NODEFAULTRESOURCEDEF`
``ImageCms.FLAGS["GRIDPOINTS"]``              :py:attr:`.ImageCms.Flags.GRIDPOINTS()`
``ImageCms.versions()``                       :py:func:`PIL.features.version_module` with
                                              ``feature="littlecms2"``, :py:data:`sys.version` or
                                              :py:data:`sys.version_info`, and ``PIL.__version__``
============================================  ====================================================

ImageMath.eval()
^^^^^^^^^^^^^^^^

``ImageMath.eval()`` has been deprecated. Use :py:meth:`~PIL.ImageMath.lambda_eval` or
:py:meth:`~PIL.ImageMath.unsafe_eval` instead. See earlier security notes for more
information.

API changes
===========

Added alpha_quality argument when saving WebP images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When saving WebP images, an ``alpha_quality`` argument can be passed to the encoder. It
is an integer value between 0 to 100, where values other than 100 will provide lossy
compression.

Negative kmeans error
^^^^^^^^^^^^^^^^^^^^^

When calling :py:meth:`~PIL.Image.Image.quantize`, a negative ``kmeans`` will now
raise a :py:exc:`ValueError`, unless a palette is supplied to make the value redundant.

Negative P1-P3 PPM value error
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a P1-P3 PPM image contains a negative value, a :py:exc:`ValueError` will now be
raised.

API additions
=============

Added PerspectiveTransform
^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`~PIL.ImageTransform.PerspectiveTransform` has been added, meaning
that all of the :py:data:`~PIL.Image.Transform` values now have a corresponding
subclass of :py:class:`~PIL.ImageTransform.Transform`.

Other changes
=============

Portable FloatMap (PFM) images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Support has been added for reading and writing grayscale (Pf format)
Portable FloatMap (PFM) files containing ``F`` data.

Release GIL when fetching WebP frames
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python's Global Interpreter Lock is now released when fetching WebP frames from
the libwebp decoder.

Type hints
^^^^^^^^^^

Pillow now has type hints for a large part of its modules, and the package
includes a ``py.typed`` file and the ``Typing :: Typed`` Trove classifier.
