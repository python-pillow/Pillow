.. py:module:: PIL.ImageWin
.. py:currentmodule:: PIL.ImageWin

:py:mod:`~PIL.ImageWin` Module (Windows-only)
=============================================

The :py:mod:`~PIL.ImageWin` module contains support to create and display images on
Windows.

ImageWin can be used with PythonWin and other user interface toolkits that
provide access to Windows device contexts or window handles. For example,
Tkinter makes the window handle available via the winfo_id method::

    from PIL import ImageWin

    dib = ImageWin.Dib(...)

    hwnd = ImageWin.HWND(widget.winfo_id())
    dib.draw(hwnd, xy)


.. autoclass:: PIL.ImageWin.Dib
    :members:

.. autoclass:: PIL.ImageWin.HDC
    :members:

.. autoclass:: PIL.ImageWin.HWND
    :members:
