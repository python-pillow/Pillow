.. py:module:: PIL.ImageStat
.. py:currentmodule:: PIL.ImageStat

:py:mod:`~PIL.ImageStat` Module
===============================

The :py:mod:`~PIL.ImageStat` module calculates global statistics for an image, or
for a region of an image.

.. py:class:: Stat(image_or_list, mask=None)

    Calculate statistics for the given image. If a mask is included,
    only the regions covered by that mask are included in the
    statistics. You can also pass in a previously calculated histogram.

    :param image: A PIL image, or a precalculated histogram.
    :param mask: An optional mask.

    .. py:attribute:: extrema

        Min/max values for each band in the image.

        .. note::

            This relies on the :py:meth:`~PIL.Image.Image.histogram` method, and
            simply returns the low and high bins used. This is correct for
            images with 8 bits per channel, but fails for other modes such as
            ``I`` or ``F``. Instead, use :py:meth:`~PIL.Image.Image.getextrema` to
            return per-band extrema for the image. This is more correct and
            efficient because, for non-8-bit modes, the histogram method uses
            :py:meth:`~PIL.Image.Image.getextrema` to determine the bins used.

    .. py:attribute:: count

        Total number of pixels for each band in the image.

    .. py:attribute:: sum

        Sum of all pixels for each band in the image.

    .. py:attribute:: sum2

        Squared sum of all pixels for each band in the image.

    .. py:attribute:: mean

        Average (arithmetic mean) pixel level for each band in the image.

    .. py:attribute:: median

        Median pixel level for each band in the image.

    .. py:attribute:: rms

        RMS (root-mean-square) for each band in the image.

    .. py:attribute:: var

        Variance for each band in the image.

    .. py:attribute:: stddev

        Standard deviation for each band in the image.
