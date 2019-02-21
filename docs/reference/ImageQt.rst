.. py:module:: PIL.ImageQt
.. py:currentmodule:: PIL.ImageQt

:py:mod:`ImageQt` Module
========================

The :py:mod:`ImageQt` module contains support for creating PyQt4, PyQt5, PySide or
PySide2 QImage objects from PIL images.

Qt 4 reached end-of-life on 2015-12-19. Its Python bindings are also EOL: PyQt4 since
2018-08-31 and PySide since 2015-10-14.

Support for PyQt4 and PySide is deprecated since Pillow 6.0.0 and will be removed in a
future version. Please upgrade to PyQt5 or PySide2.

.. versionadded:: 1.1.6

.. py:class:: ImageQt.ImageQt(image)

    Creates an :py:class:`~PIL.ImageQt.ImageQt` object from a PIL
    :py:class:`~PIL.Image.Image` object. This class is a subclass of
    QtGui.QImage, which means that you can pass the resulting objects directly
    to PyQt4/PyQt5/PySide API functions and methods.

    This operation is currently supported for mode 1, L, P, RGB, and RGBA
    images. To handle other modes, you need to convert the image first.
