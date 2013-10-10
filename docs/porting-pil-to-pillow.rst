Porting existing PIL-based code to Pillow
=========================================

Pillow is a functional drop-in replacement for the Python Imaging Library. To
run your existing PIL-compatible code with Pillow, it needs to be modified to
import the ``Imaging`` module from the ``PIL`` namespace *instead* of the
global namespace. Change this::

    import Image

to this::

    from PIL import Image

The :py:mod:`_imaging` module has been moved. You can now import it like this::

    from PIL.Image import core as _imaging
