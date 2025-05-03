Internal modules
================

:mod:`~PIL._binary` module
--------------------------

.. automodule:: PIL._binary
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`~PIL._deprecate` module
-----------------------------

.. automodule:: PIL._deprecate
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`~PIL._tkinter_finder` module
----------------------------------

.. automodule:: PIL._tkinter_finder
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`~PIL._typing` module
--------------------------

.. module:: PIL._typing

Provides a convenient way to import type hints that are not available
on some Python versions.

.. py:class:: Buffer

    Typing alias.

.. py:class:: IntegralLike

    Typing alias.

.. py:class:: NumpyArray

    Typing alias.

.. py:class:: StrOrBytesPath

    Typing alias.

.. py:class:: SupportsRead

    An object that supports the read method.

.. py:data:: TypeGuard
    :value: typing.TypeGuard

    See :py:obj:`typing.TypeGuard`.

:mod:`~PIL._util` module
------------------------

.. automodule:: PIL._util
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`~PIL._version` module
---------------------------

.. module:: PIL._version

.. data:: __version__
    :annotation:
    :type: str

    This is the master version number for Pillow,
    all other uses reference this module.

:mod:`PIL.Image.core` module
----------------------------

.. module:: PIL._imaging
.. module:: PIL.Image.core

An internal interface module previously known as :mod:`~PIL._imaging`,
implemented in :file:`_imaging.c`.

.. py:class:: ImagingCore

    A representation of the image data.
