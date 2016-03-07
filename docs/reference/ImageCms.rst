.. py:module:: PIL.ImageCms
.. py:currentmodule:: PIL.ImageCms

:py:mod:`ImageCms` Module
=========================

The :py:mod:`ImageCms` module provides color profile management
support using the LittleCMS2 color management engine, based on Kevin
Cazabon's PyCMS library.

.. automodule:: PIL.ImageCms
    :members:
    :noindex:

CmsProfile
----------

The ICC color profiles are wrapped in an instance of the class
:py:class:`CmsProfile`.  The specification ICC.1:2010 contains more
information about the meaning of the values in ICC profiles.

For convenience, all XYZ-values are also given as xyY-values (so they
can be easily displayed in a chromaticity diagram, for example).

.. py:class:: CmsProfile

    .. py:attribute:: creation_date

        Date and time this profile was first created (see 7.2.1 of ICC.1:2010).

        :type: :py:class:`datetime.datetime` or ``None``

    .. py:attribute:: version

        The version number of the ICC standard that this profile follows
        (e.g. `2.0`).

        :type: :py:class:`float`

    .. py:attribute:: icc_version

        Same as `version`, but in encoded format (see 7.2.4 of ICC.1:2010).

    .. py:attribute:: device_class

        4-character string identifying the profile class.  One of
        ``scnr``, ``mntr``, ``prtr``, ``link``, ``spac``, ``abst``,
        ``nmcl`` (see 7.2.5 of ICC.1:2010 for details).

        :type: :py:class:`string`

    .. py:attribute:: xcolor_space

        4-character string (padded with whitespace) identifying the color
        space, e.g. ``XYZ␣``, ``RGB␣`` or ``CMYK`` (see 7.2.6 of
        ICC.1:2010 for details).

        Note that the deprecated attribute ``color_space`` contains an
        interpreted (non-padded) variant of this (but can be empty on
        unknown input).

        :type: :py:class:`string`

    .. py:attribute:: connection_space

        4-character string (padded with whitespace) identifying the color
        space on the B-side of the transform (see 7.2.7 of ICC.1:2010 for
        details).

        Note that the deprecated attribute ``pcs`` contains an interpreted
        (non-padded) variant of this (but can be empty on unknown input).

        :type: :py:class:`string`

    .. py:attribute:: header_flags

        The encoded header flags of the profile (see 7.2.11 of ICC.1:2010
        for details).

        :type: :py:class:`int`

    .. py:attribute:: header_manufacturer

        4-character string (padded with whitespace) identifying the device
        manufacturer, which shall match the signature contained in the
        appropriate section of the ICC signature registry found at
        www.color.org (see 7.2.12 of ICC.1:2010).

        :type: :py:class:`string`

    .. py:attribute:: header_model

        4-character string (padded with whitespace) identifying the device
        model, which shall match the signature contained in the
        appropriate section of the ICC signature registry found at
        www.color.org (see 7.2.13 of ICC.1:2010).

        :type: :py:class:`string`

    .. py:attribute:: attributes

        Flags used to identify attributes unique to the particular device
        setup for which the profile is applicable (see 7.2.14 of
        ICC.1:2010 for details).

        :type: :py:class:`int`

    .. py:attribute:: rendering_intent

        The rendering intent to use when combining this profile with
        another profile (usually overridden at run-time, but provided here
        for DeviceLink and embedded source profiles, see 7.2.15 of ICC.1:2010).

        One of ``ImageCms.INTENT_ABSOLUTE_COLORIMETRIC``, ``ImageCms.INTENT_PERCEPTUAL``,
        ``ImageCms.INTENT_RELATIVE_COLORIMETRIC`` and ``ImageCms.INTENT_SATURATION``.

        :type: :py:class:`int`

    .. py:attribute:: profile_id

        A sequence of 16 bytes identifying the profile (via a specially
        constructed MD5 sum), or 16 binary zeroes if the profile ID has
        not been calculated (see 7.2.18 of ICC.1:2010).

        :type: :py:class:`bytes`

    .. py:attribute:: copyright

        The text copyright information for the profile (see 9.2.21 of ICC.1:2010).

        :type: :py:class:`unicode` or ``None``

    .. py:attribute:: manufacturer

        The (english) display string for the device manufacturer (see
        9.2.22 of ICC.1:2010).

        :type: :py:class:`unicode` or ``None``

    .. py:attribute:: model

        The (english) display string for the device model of the device
        for which this profile is created (see 9.2.23 of ICC.1:2010).

        :type: :py:class:`unicode` or ``None``

    .. py:attribute:: profile_description

        The (english) display string for the profile description (see
        9.2.41 of ICC.1:2010).

        :type: :py:class:`unicode` or ``None``

    .. py:attribute:: target

        The name of the registered characterization data set, or the
        measurement data for a characterization target (see 9.2.14 of
        ICC.1:2010).

        :type: :py:class:`unicode` or ``None``

    .. py:attribute:: red_colorant

        The first column in the matrix used in matrix/TRC transforms (see 9.2.44 of ICC.1:2010).

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: green_colorant

        The second column in the matrix used in matrix/TRC transforms (see 9.2.30 of ICC.1:2010).

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: blue_colorant

        The third column in the matrix used in matrix/TRC transforms (see 9.2.4 of ICC.1:2010).

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: luminance

        The absolute luminance of emissive devices in candelas per square
        metre as described by the Y channel (see 9.2.32 of ICC.1:2010).

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: chromaticity

        The data of the phosphor/colorant chromaticity set used (red,
        green and blue channels, see 9.2.16 of ICC.1:2010).

        :type: ``((x, y, Y), (x, y, Y), (x, y, Y))`` or ``None``

    .. py:attribute:: chromatic_adaption

        The chromatic adaption matrix converts a color measured using the
        actual illumination conditions and relative to the actual adopted
        white, to an color relative to the PCS adopted white, with
        complete adaptation from the actual adopted white chromaticity to
        the PCS adopted white chromaticity (see 9.2.15 of ICC.1:2010).

        Two matrices are returned, one in (X, Y, Z) space and one in (x, y, Y) space.

        :type: 2-tuple of 3-tuple, the first with (X, Y, Z) and the second with (x, y, Y) values

    .. py:attribute:: colorant_table

        This tag identifies the colorants used in the profile by a unique
        name and set of PCSXYZ or PCSLAB values (see 9.2.19 of
        ICC.1:2010).

        :type: list of strings

    .. py:attribute:: colorant_table_out

        This tag identifies the colorants used in the profile by a unique
        name and set of PCSLAB values (for DeviceLink profiles only, see
        9.2.19 of ICC.1:2010).

        :type: list of strings

    .. py:attribute:: colorimetric_intent

        4-character string (padded with whitespace) identifying the image
        state of PCS colorimetry produced using the colorimetric intent
        transforms (see 9.2.20 of ICC.1:2010 for details).

        :type: :py:class:`string` or ``None``

    .. py:attribute:: perceptual_rendering_intent_gamut

        4-character string (padded with whitespace) identifying the (one)
        standard reference medium gamut (see 9.2.37 of ICC.1:2010 for
        details).

        :type: :py:class:`string` or ``None``

    .. py:attribute:: saturation_rendering_intent_gamut

        4-character string (padded with whitespace) identifying the (one)
        standard reference medium gamut (see 9.2.37 of ICC.1:2010 for
        details).

        :type: :py:class:`string` or ``None``

    .. py:attribute:: technology

        4-character string (padded with whitespace) identifying the device
        technology (see 9.2.47 of ICC.1:2010 for details).

        :type: :py:class:`string` or ``None``

    .. py:attribute:: media_black_point

        This tag specifies the media black point and is used for
        generating absolute colorimetry.

        This tag was available in ICC 3.2, but it is removed from
        version 4.

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: media_white_point_temperature

        Calculates the white point temperature (see the LCMS documentation
        for more information).

        :type: :py:class:`float` or `None`

    .. py:attribute:: viewing_condition

        The (english) display string for the viewing conditions (see
        9.2.48 of ICC.1:2010).

        :type: :py:class:`unicode` or ``None``

    .. py:attribute:: screening_description

        The (english) display string for the screening conditions.

        This tag was available in ICC 3.2, but it is removed from
        version 4.

        :type: :py:class:`unicode` or ``None``

    .. py:attribute:: red_primary

        The XYZ-transformed of the RGB primary color red (1, 0, 0).

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: green_primary

        The XYZ-transformed of the RGB primary color green (0, 1, 0).

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: blue_primary

        The XYZ-transformed of the RGB primary color blue (0, 0, 1).

        :type: ``((X, Y, Z), (x, y, Y))`` or ``None``

    .. py:attribute:: is_matrix_shaper

        True if this profile is implemented as a matrix shaper (see
        documentation on LCMS).

        :type: :py:class:`bool`

    .. py:attribute:: clut

        Returns a dictionary of all supported intents and directions for
        the CLUT model.

        The dictionary is indexed by intents
        (``ImageCms.INTENT_ABSOLUTE_COLORIMETRIC``,
        ``ImageCms.INTENT_PERCEPTUAL``,
        ``ImageCms.INTENT_RELATIVE_COLORIMETRIC`` and
        ``ImageCms.INTENT_SATURATION``).

        The values are 3-tuples indexed by directions
        (``ImageCms.DIRECTION_INPUT``, ``ImageCms.DIRECTION_OUTPUT``,
        ``ImageCms.DIRECTION_PROOF``).

        The elements of the tuple are booleans.  If the value is ``True``,
        that intent is supported for that direction.

        :type: :py:class:`dict` of boolean 3-tuples

    .. py:attribute:: intent_supported

        Returns a dictionary of all supported intents and directions.

        The dictionary is indexed by intents
        (``ImageCms.INTENT_ABSOLUTE_COLORIMETRIC``,
        ``ImageCms.INTENT_PERCEPTUAL``,
        ``ImageCms.INTENT_RELATIVE_COLORIMETRIC`` and
        ``ImageCms.INTENT_SATURATION``).

        The values are 3-tuples indexed by directions
        (``ImageCms.DIRECTION_INPUT``, ``ImageCms.DIRECTION_OUTPUT``,
        ``ImageCms.DIRECTION_PROOF``).

        The elements of the tuple are booleans.  If the value is ``True``,
        that intent is supported for that direction.

        :type: :py:class:`dict` of boolean 3-tuples

    .. py:attribute:: color_space

        Deprecated but retained for backwards compatibility.
        Interpreted value of :py:attr:`.xcolor_space`.  May be the
        empty string if value could not be decoded.

        :type: :py:class:`string`

    .. py:attribute:: pcs

        Deprecated but retained for backwards compatibility.
        Interpreted value of :py:attr:`.connection_space`.  May be
        the empty string if value could not be decoded.

        :type: :py:class:`string`

    .. py:attribute:: product_model

        Deprecated but retained for backwards compatibility.
        ASCII-encoded value of :py:attr:`.model`.

        :type: :py:class:`string`

    .. py:attribute:: product_manufacturer

        Deprecated but retained for backwards compatibility.
        ASCII-encoded value of :py:attr:`.manufacturer`.

        :type: :py:class:`string`

    .. py:attribute:: product_copyright

        Deprecated but retained for backwards compatibility.
        ASCII-encoded value of :py:attr:`.copyright`.

        :type: :py:class:`string`

    .. py:attribute:: product_description

        Deprecated but retained for backwards compatibility.
        ASCII-encoded value of :py:attr:`.profile_description`.

        :type: :py:class:`string`

    .. py:attribute:: product_desc

        Deprecated but retained for backwards compatibility.
        ASCII-encoded value of :py:attr:`.profile_description`.

        This alias of :py:attr:`.product_description` used to
        contain a derived informative string about the profile,
        depending on the value of the description, copyright,
        manufacturer and model fields).

        :type: :py:class:`string`

    There is one function defined on the class:

    .. py:method:: is_intent_supported(intent, direction)

        Returns if the intent is supported for the given direction.

        Note that you can also get this information for all intents and directions
        with :py:attr:`.intent_supported`.

        :param intent: One of ``ImageCms.INTENT_ABSOLUTE_COLORIMETRIC``,
    		   ``ImageCms.INTENT_PERCEPTUAL``,
    		   ``ImageCms.INTENT_RELATIVE_COLORIMETRIC``
    		   and ``ImageCms.INTENT_SATURATION``.
        :param direction: One of ``ImageCms.DIRECTION_INPUT``,
    		      ``ImageCms.DIRECTION_OUTPUT``
    		      and ``ImageCms.DIRECTION_PROOF``
        :return: Boolean if the intent and direction is supported.
