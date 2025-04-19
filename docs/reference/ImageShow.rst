.. py:module:: PIL.ImageShow
.. py:currentmodule:: PIL.ImageShow

:py:mod:`~PIL.ImageShow` module
===============================

The :py:mod:`~PIL.ImageShow` module is used to display images.
All default viewers convert the image to be shown to PNG format.

.. autofunction:: PIL.ImageShow.show

.. autoclass:: IPythonViewer
.. autoclass:: WindowsViewer
.. autoclass:: MacViewer

.. class:: UnixViewer

    The following viewers may be registered on Unix-based systems, if the given command is found:

    .. autoclass:: PIL.ImageShow.XDGViewer
    .. autoclass:: PIL.ImageShow.DisplayViewer
    .. autoclass:: PIL.ImageShow.GmDisplayViewer
    .. autoclass:: PIL.ImageShow.EogViewer
    .. autoclass:: PIL.ImageShow.XVViewer

    To provide maximum functionality on Unix-based systems, temporary files created
    from images will not be automatically removed by Pillow.

.. autofunction:: PIL.ImageShow.register
.. autoclass:: PIL.ImageShow.Viewer
    :member-order: bysource
    :members:
    :undoc-members:
