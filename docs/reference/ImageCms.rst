.. py:module:: PIL.ImageCms
.. py:currentmodule:: PIL.ImageCms

:py:mod:`~PIL.ImageCms` Module
==============================

The :py:mod:`~PIL.ImageCms` module provides color profile management
support using the LittleCMS2 color management engine, based on Kevin
Cazabon's PyCMS library.

.. autoclass:: ImageCmsTransform
.. autoexception:: PyCMSError

Functions
---------

.. autofunction:: applyTransform
.. autofunction:: buildProofTransform
.. autofunction:: buildProofTransformFromOpenProfiles
.. autofunction:: buildTransform
.. autofunction:: buildTransformFromOpenProfiles
.. autofunction:: createProfile
.. autofunction:: getDefaultIntent
.. autofunction:: getOpenProfile
.. autofunction:: getProfileCopyright
.. autofunction:: getProfileDescription
.. autofunction:: getProfileInfo
.. autofunction:: getProfileManufacturer
.. autofunction:: getProfileModel
.. autofunction:: getProfileName
.. autofunction:: get_display_profile
.. autofunction:: isIntentSupported
.. autofunction:: profileToProfile
.. autofunction:: versions

CmsProfile
----------

The ICC color profiles are wrapped in an instance of the class
:py:class:`CmsProfile`.  The specification ICC.1:2010 contains more
information about the meaning of the values in ICC profiles.

For convenience, all XYZ-values are also given as xyY-values (so they
can be easily displayed in a chromaticity diagram, for example).

.. py:class:: CmsProfile

    .. py:attribute:: creation_date
        :type: Optional[datetime.datetime]

        Date and time this profile was first created (see 7.2.1 of ICC.1:2010).

    .. py:attribute:: version
        :type: float

        The version number of the ICC standard that this profile follows
        (e.g. ``2.0``).

    .. py:attribute:: icc_version
        :type: int

        Same as ``version``, but in encoded format (see 7.2.4 of ICC.1:2010).

    .. py:attribute:: device_class
        :type: str

        4-character string identifying the profile class.  One of
        ``scnr``, ``mntr``, ``prtr``, ``link``, ``spac``, ``abst``,
        ``nmcl`` (see 7.2.5 of ICC.1:2010 for details).

    .. py:attribute:: xcolor_space
        :type: str

        4-character string (padded with whitespace) identifying the color
        space, e.g. ``XYZ␣``, ``RGB␣`` or ``CMYK`` (see 7.2.6 of
        ICC.1:2010 for details).

    .. py:attribute:: connection_space
        :type: str

        4-character string (padded with whitespace) identifying the color
        space on the B-side of the transform (see 7.2.7 of ICC.1:2010 for
        details).

    .. py:attribute:: header_flags
        :type: int

        The encoded header flags of the profile (see 7.2.11 of ICC.1:2010
        for details).

    .. py:attribute:: header_manufacturer
        :type: str

        4-character string (padded with whitespace) identifying the device
        manufacturer, which shall match the signature contained in the
        appropriate section of the ICC signature registry found at
        www.color.org (see 7.2.12 of ICC.1:2010).

    .. py:attribute:: header_model
        :type: str

        4-character string (padded with whitespace) identifying the device
        model, which shall match the signature contained in the
        appropriate section of the ICC signature registry found at
        www.color.org (see 7.2.13 of ICC.1:2010).

    .. py:attribute:: attributes
        :type: int

        Flags used to identify attributes unique to the particular device
        setup for which the profile is applicable (see 7.2.14 of
        ICC.1:2010 for details).

    .. py:attribute:: rendering_intent
        :type: int

        The rendering intent to use when combining this profile with
        another profile (usually overridden at run-time, but provided here
        for DeviceLink and embedded source profiles, see 7.2.15 of ICC.1:2010).

        One of ``ImageCms.INTENT_ABSOLUTE_COLORIMETRIC``, ``ImageCms.INTENT_PERCEPTUAL``,
        ``ImageCms.INTENT_RELATIVE_COLORIMETRIC`` and ``ImageCms.INTENT_SATURATION``.

    .. py:attribute:: profile_id
        :type: bytes

        A sequence of 16 bytes identifying the profile (via a specially
        constructed MD5 sum), or 16 binary zeroes if the profile ID has
        not been calculated (see 7.2.18 of ICC.1:2010).

    .. py:attribute:: copyright
        :type: Optional[str]

        The text copyright information for the profile (see 9.2.21 of ICC.1:2010).

    .. py:attribute:: manufacturer
        :type: Optional[str]

        The (English) display string for the device manufacturer (see
        9.2.22 of ICC.1:2010).

    .. py:attribute:: model
        :type: Optional[str]

        The (English) display string for the device model of the device
        for which this profile is created (see 9.2.23 of ICC.1:2010).

    .. py:attribute:: profile_description
        :type: Optional[str]

        The (English) display string for the profile description (see
        9.2.41 of ICC.1:2010).

    .. py:attribute:: target
        :type: Optional[str]

        The name of the registered characterization data set, or the
        measurement data for a characterization target (see 9.2.14 of
        ICC.1:2010).

    .. py:attribute:: red_colorant
        :type: Optional[tuple[tuple[float]]]

        The first column in the matrix used in matrix/TRC transforms (see 9.2.44 of ICC.1:2010).

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: green_colorant
        :type: Optional[tuple[tuple[float]]]

        The second column in the matrix used in matrix/TRC transforms (see 9.2.30 of ICC.1:2010).

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: blue_colorant
        :type: Optional[tuple[tuple[float]]]

        The third column in the matrix used in matrix/TRC transforms (see 9.2.4 of ICC.1:2010).

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: luminance
        :type: Optional[tuple[tuple[float]]]

        The absolute luminance of emissive devices in candelas per square
        metre as described by the Y channel (see 9.2.32 of ICC.1:2010).

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: chromaticity
        :type: Optional[tuple[tuple[float]]]

        The data of the phosphor/colorant chromaticity set used (red,
        green and blue channels, see 9.2.16 of ICC.1:2010).

        The value is in the format ``((x, y, Y), (x, y, Y), (x, y, Y))``, if available.

    .. py:attribute:: chromatic_adaption
        :type: tuple[tuple[float]]

        The chromatic adaption matrix converts a color measured using the
        actual illumination conditions and relative to the actual adopted
        white, to a color relative to the PCS adopted white, with
        complete adaptation from the actual adopted white chromaticity to
        the PCS adopted white chromaticity (see 9.2.15 of ICC.1:2010).

        Two 3-tuples of floats are returned in a 2-tuple,
        one in (X, Y, Z) space and one in (x, y, Y) space.

    .. py:attribute:: colorant_table
        :type: list[str]

        This tag identifies the colorants used in the profile by a unique
        name and set of PCSXYZ or PCSLAB values (see 9.2.19 of
        ICC.1:2010).

    .. py:attribute:: colorant_table_out
        :type: list[str]

        This tag identifies the colorants used in the profile by a unique
        name and set of PCSLAB values (for DeviceLink profiles only, see
        9.2.19 of ICC.1:2010).

    .. py:attribute:: colorimetric_intent
        :type: Optional[str]

        4-character string (padded with whitespace) identifying the image
        state of PCS colorimetry produced using the colorimetric intent
        transforms (see 9.2.20 of ICC.1:2010 for details).

    .. py:attribute:: perceptual_rendering_intent_gamut
        :type: Optional[str]

        4-character string (padded with whitespace) identifying the (one)
        standard reference medium gamut (see 9.2.37 of ICC.1:2010 for
        details).

    .. py:attribute:: saturation_rendering_intent_gamut
        :type: Optional[str]

        4-character string (padded with whitespace) identifying the (one)
        standard reference medium gamut (see 9.2.37 of ICC.1:2010 for
        details).

    .. py:attribute:: technology
        :type: Optional[str]

        4-character string (padded with whitespace) identifying the device
        technology (see 9.2.47 of ICC.1:2010 for details).

    .. py:attribute:: media_black_point
        :type: Optional[tuple[tuple[float]]]

        This tag specifies the media black point and is used for
        generating absolute colorimetry.

        This tag was available in ICC 3.2, but it is removed from
        version 4.

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: media_white_point_temperature
        :type: Optional[float]

        Calculates the white point temperature (see the LCMS documentation
        for more information).

    .. py:attribute:: viewing_condition
        :type: Optional[str]

        The (English) display string for the viewing conditions (see
        9.2.48 of ICC.1:2010).

    .. py:attribute:: screening_description
        :type: Optional[str]

        The (English) display string for the screening conditions.

        This tag was available in ICC 3.2, but it is removed from
        version 4.

    .. py:attribute:: red_primary
        :type: Optional[tuple[tuple[float]]]

        The XYZ-transformed of the RGB primary color red (1, 0, 0).

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: green_primary
        :type: Optional[tuple[tuple[float]]]

        The XYZ-transformed of the RGB primary color green (0, 1, 0).

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: blue_primary
        :type: Optional[tuple[tuple[float]]]

        The XYZ-transformed of the RGB primary color blue (0, 0, 1).

        The value is in the format ``((X, Y, Z), (x, y, Y))``, if available.

    .. py:attribute:: is_matrix_shaper
        :type: bool

        True if this profile is implemented as a matrix shaper (see
        documentation on LCMS).

    .. py:attribute:: clut
        :type: dict[tuple[bool]]

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

    .. py:attribute:: intent_supported
        :type: dict[tuple[bool]]

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
