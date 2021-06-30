.. py:module:: PIL.ImageShow
.. py:currentmodule:: PIL.ImageShow

:py:mod:`~PIL.ImageShow` Module
===============================

The :py:mod:`~PIL.ImageShow` Module is used to display images.
All default viewers convert the image to be shown to PNG format.

.. autofunction:: PIL.ImageShow.show

.. autoclass:: IPythonViewer
.. autoclass:: WindowsViewer
.. autoclass:: MacViewer

.. class:: UnixViewer

    The following viewers may be registered on Unix-based systems, if the given command is found:

    .. autoclass:: PIL.ImageShow.DisplayViewer
    .. autoclass:: PIL.ImageShow.GmDisplayViewer
    .. autoclass:: PIL.ImageShow.EogViewer
    .. autoclass:: PIL.ImageShow.XVViewer

.. autofunction:: PIL.ImageShow.register
.. autoclass:: PIL.ImageShow.Viewer
    :member-order: bysource
    :members:
    :undoc-members:
