9.0.1
-----

Security
========

This release addresses several security problems.

:cve:`2022-24303`: Temp image removal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the path to the temporary directory on Linux or macOS
contained a space, this would break removal of the temporary image file after
``im.show()`` (and related actions), and potentially remove an unrelated file. This
has been present since PIL.

:cve:`2022-22817`: Restrict lambda expressions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While Pillow 9.0 restricted top-level builtins available to
:py:meth:`!PIL.ImageMath.eval`, it did not prevent builtins
available to lambda expressions. These are now also restricted.

Other changes
=============

Pillow 9.0 added support for ``xdg-open`` as an image viewer, but there have been
reports that the temporary image file was removed too quickly to be loaded into the
final application. A delay has been added.
