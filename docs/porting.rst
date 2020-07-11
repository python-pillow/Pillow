Porting
=======

**Porting existing PIL-based code to Pillow**

Pillow is a functional drop-in replacement for the Python Imaging Library.

PIL is Python 2 only. Pillow dropped support for Python 2 in Pillow
7.0. So if you would like to run the latest version of Pillow, you will first
and foremost need to port your code from Python 2 to 3.

To run your existing PIL-compatible code with Pillow, it needs to be modified
to import the ``Image`` module from the ``PIL`` namespace *instead* of the
global namespace. Change this::

    import Image

to this::

    from PIL import Image

The :py:mod:`PIL._imaging` module has been moved to :py:mod:`PIL.Image.core`.
You can now import it like this::

    from PIL.Image import core as _imaging

The image plugin loading mechanism has changed. Pillow no longer
automatically imports any file in the Python path with a name ending
in :file:`ImagePlugin.py`. You will need to import your image plugin
manually.

Pillow will raise an exception if the core extension can't be loaded
for any reason, including a version mismatch between the Python and
extension code. Previously PIL allowed Python only code to run if the
core extension was not available.
