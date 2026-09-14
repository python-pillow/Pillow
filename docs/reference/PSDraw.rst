.. py:module:: PIL.PSDraw
.. py:currentmodule:: PIL.PSDraw

:py:mod:`~PIL.PSDraw` module
============================

The :py:mod:`~PIL.PSDraw` module provides simple print support for PostScript
printers. You can print text, graphics and images through this module.

By default, :py:meth:`~PIL.PSDraw.PSDraw.text` preserves PostScript backslash
escape sequences and escapes parentheses as before. Pass the keyword-only boolean
``escape=True`` to escape backslashes as well, for example when drawing a Windows
path::

    ps.text((10, 20), r"C:\temp\new", escape=True)

Text is encoded as Latin-1. PostScript normalizes literal CR and CRLF line endings
to LF, including when ``escape=True``.

.. autoclass:: PIL.PSDraw.PSDraw
    :members:
