.. py:module:: PIL.ImagePath
.. py:currentmodule:: PIL.ImagePath

:py:mod:`~PIL.ImagePath` Module
===============================

The :py:mod:`~PIL.ImagePath` module is used to store and manipulate 2-dimensional
vector data. Path objects can be passed to the methods on the
:py:mod:`~PIL.ImageDraw` module.

.. py:class:: PIL.ImagePath.Path

    A path object. The coordinate list can be any sequence object containing
    either 2-tuples [(x, y), …] or numeric values [x, y, …].

    You can also create a path object from another path object.

    In 1.1.6 and later, you can also pass in any object that implements
    Python’s buffer API. The buffer should provide read access, and contain C
    floats in machine byte order.

    The path object implements most parts of the Python sequence interface, and
    behaves like a list of (x, y) pairs. You can use len(), item access, and
    slicing as usual. However, the current version does not support slice
    assignment, or item and slice deletion.

    :param xy: A sequence. The sequence can contain 2-tuples [(x, y), ...]
               or a flat list of numbers [x, y, ...].

.. py:method:: PIL.ImagePath.Path.compact(distance=2)

    Compacts the path, by removing points that are close to each other. This
    method modifies the path in place, and returns the number of points left in
    the path.

    ``distance`` is measured as `Manhattan distance`_ and defaults to two
    pixels.

.. _Manhattan distance: https://en.wikipedia.org/wiki/Manhattan_distance

.. py:method:: PIL.ImagePath.Path.getbbox()

    Gets the bounding box of the path.

    :return: ``(x0, y0, x1, y1)``

.. py:method:: PIL.ImagePath.Path.map(function)

    Maps the path through a function.

.. py:method:: PIL.ImagePath.Path.tolist(flat=0)

    Converts the path to a Python list [(x, y), …].

    :param flat: By default, this function returns a list of 2-tuples
                 [(x, y), ...].  If this argument is ``True``, it
                 returns a flat list [x, y, ...] instead.
    :return: A list of coordinates. See ``flat``.

.. py:method:: PIL.ImagePath.Path.transform(matrix)

    Transforms the path in place, using an affine transform. The matrix is a
    6-tuple (a, b, c, d, e, f), and each point is mapped as follows:

    .. code-block:: python

        xOut = xIn * a + yIn * b + c
        yOut = xIn * d + yIn * e + f
