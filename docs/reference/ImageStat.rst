.. py:module:: PIL.ImageStat
.. py:currentmodule:: PIL.ImageStat

:py:mod:`ImageStat` Module
==========================

The :py:mod:`ImageStat` module calculates global statistics for an image, or
for a region of an image.

.. py:class:: PIL.ImageStat.Stat(image_or_list, mask=None)

    Calculate statistics for the given image. If a mask is included,
    only the regions covered by that mask are included in the
    statistics. You can also pass in a previously calculated histogram.

    :param image: A PIL image, or a precalculated histogram.
    :param mask: An optional mask.

    .. py:attribute:: extrema

        Min/max values for each band in the image.

    .. py:attribute:: count

        Total number of pixels.

    .. py:attribute:: sum

        Sum of all pixels.

    .. py:attribute:: sum2

        Squared sum of all pixels.

    .. py:attribute:: pixel

        Average pixel level.

    .. py:attribute:: median

        Median pixel level.

    .. py:attribute:: rms

        RMS (root-mean-square).

    .. py:attribute:: var

        Variance.

    .. py:attribute:: stddev

        Standard deviation.
