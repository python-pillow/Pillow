.. py:module:: PIL.ImageQt
.. py:currentmodule:: PIL.ImageQt

:py:mod:`~PIL.ImageQt` module
=============================

The :py:mod:`~PIL.ImageQt` module contains support for creating PyQt6 or PySide6
QImage objects from PIL images.

.. versionadded:: 1.1.6

.. py:class:: ImageQt(image)

    Creates an :py:class:`~PIL.ImageQt.ImageQt` object from a PIL
    :py:class:`~PIL.Image.Image` object. This class is a subclass of
    QtGui.QImage, which means that you can pass the resulting objects directly
    to PyQt6/PySide6 API functions and methods.

    This operation is currently supported for mode 1, L, P, RGB, and RGBA
    images. To handle other modes, you need to convert the image first.
