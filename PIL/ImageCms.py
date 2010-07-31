#
# The Python Imaging Library.
# $Id$
#
# optional color managment support, based on Kevin Cazabon's PyCMS
# library.
#
# History:
# 2009-03-08 fl   Added to PIL.
#
# Copyright (C) 2002-2003 Kevin Cazabon
# Copyright (c) 2009 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.  See
# below for the original description.
#

DESCRIPTION = """
pyCMS

    a Python / PIL interface to the littleCMS ICC Color Management System
    Copyright (C) 2002-2003 Kevin Cazabon
    kevin@cazabon.com
    http://www.cazabon.com

    pyCMS home page:  http://www.cazabon.com/pyCMS
    littleCMS home page:  http://www.littlecms.com
    (littleCMS is Copyright (C) 1998-2001 Marti Maria)

    Originally released under LGPL.  Graciously donated to PIL in
    March 2009, for distribution under the standard PIL license

    The pyCMS.py module provides a "clean" interface between Python/PIL and
    pyCMSdll, taking care of some of the more complex handling of the direct
    pyCMSdll functions, as well as error-checking and making sure that all
    relevant data is kept together.

    While it is possible to call pyCMSdll functions directly, it's not highly
    recommended.

    Version History:

        0.1.0 pil mod   March 10, 2009

                        Renamed display profile to proof profile. The proof
                        profile is the profile of the device that is being
                        simulated, not the profile of the device which is
                        actually used to display/print the final simulation
                        (that'd be the output profile) - also see LCMSAPI.txt
                        input colorspace -> using 'renderingIntent' -> proof
                        colorspace -> using 'proofRenderingIntent' -> output
                        colorspace

                        Added LCMS FLAGS support.
                        Added FLAGS["SOFTPROOFING"] as default flag for
                        buildProofTransform (otherwise the proof profile/intent
                        would be ignored).

        0.1.0 pil       March 2009 - added to PIL, as PIL.ImageCms

        0.0.2 alpha     Jan 6, 2002

                        Added try/except statements arount type() checks of
                        potential CObjects... Python won't let you use type()
                        on them, and raises a TypeError (stupid, if you ask me!)

                        Added buildProofTransformFromOpenProfiles() function.
                        Additional fixes in DLL, see DLL code for details.

        0.0.1 alpha     first public release, Dec. 26, 2002

    Known to-do list with current version (of Python interface, not pyCMSdll):

        none

"""

VERSION = "0.1.0 pil"

# --------------------------------------------------------------------.

import Image
import _imagingcms

core = _imagingcms

#
# intent/direction values

INTENT_PERCEPTUAL = 0
INTENT_RELATIVE_COLORIMETRIC = 1
INTENT_SATURATION = 2
INTENT_ABSOLUTE_COLORIMETRIC = 3

DIRECTION_INPUT = 0
DIRECTION_OUTPUT = 1
DIRECTION_PROOF = 2

#
# flags

FLAGS = {
    "MATRIXINPUT": 1,
    "MATRIXOUTPUT": 2,
    "MATRIXONLY": (1|2),
    "NOWHITEONWHITEFIXUP": 4, # Don't hot fix scum dot
    "NOPRELINEARIZATION": 16, # Don't create prelinearization tables on precalculated transforms (internal use)
    "GUESSDEVICECLASS": 32, # Guess device class (for transform2devicelink)
    "NOTCACHE": 64, # Inhibit 1-pixel cache
    "NOTPRECALC": 256,
    "NULLTRANSFORM": 512, # Don't transform anyway
    "HIGHRESPRECALC": 1024, # Use more memory to give better accurancy
    "LOWRESPRECALC": 2048, # Use less memory to minimize resouces
    "WHITEBLACKCOMPENSATION": 8192,
    "BLACKPOINTCOMPENSATION": 8192,
    "GAMUTCHECK": 4096, # Out of Gamut alarm
    "SOFTPROOFING": 16384, # Do softproofing
    "PRESERVEBLACK": 32768, # Black preservation
    "NODEFAULTRESOURCEDEF": 16777216, # CRD special
    "GRIDPOINTS": lambda n: ((n) & 0xFF) << 16 # Gridpoints
}

_MAX_FLAG = 0
for flag in FLAGS.values():
    if isinstance(flag, type(0)):
        _MAX_FLAG = _MAX_FLAG | flag

# --------------------------------------------------------------------.
# Experimental PIL-level API
# --------------------------------------------------------------------.

##
# Profile.

class ImageCmsProfile:

    def __init__(self, profile):
        # accepts a string (filename), a file-like object, or a low-level
        # profile object
        if Image.isStringType(profile):
            self._set(core.profile_open(profile), profile)
        elif hasattr(profile, "read"):
            self._set(core.profile_fromstring(profile.read()))
        else:
            self._set(profile) # assume it's already a profile

    def _set(self, profile, filename=None):
        self.profile = profile
        self.filename = filename
        if profile:
            self.product_name = profile.product_name
            self.product_info = profile.product_info
        else:
            self.product_name = None
            self.product_info = None

##
# Transform.  This can be used with the procedural API, or with the
# standard {@link Image.point} method.

class ImageCmsTransform(Image.ImagePointHandler):

    def __init__(self, input, output, input_mode, output_mode,
                 intent=INTENT_PERCEPTUAL,
                 proof=None, proof_intent=INTENT_ABSOLUTE_COLORIMETRIC, flags=0):
        if proof is None:
            self.transform = core.buildTransform(
                input.profile, output.profile,
                input_mode, output_mode,
                intent,
                flags
                )
        else:
            self.transform = core.buildProofTransform(
                input.profile, output.profile, proof.profile,
                input_mode, output_mode,
                intent, proof_intent,
                flags
                )
        # Note: inputMode and outputMode are for pyCMS compatibility only
        self.input_mode = self.inputMode = input_mode
        self.output_mode = self.outputMode = output_mode

    def point(self, im):
        return self.apply(im)

    def apply(self, im, imOut=None):
        im.load()
        if imOut is None:
            imOut = Image.new(self.output_mode, im.size, None)
        result = self.transform.apply(im.im.id, imOut.im.id)
        return imOut

    def apply_in_place(self, im):
        im.load()
        if im.mode != self.output_mode:
            raise ValueError("mode mismatch") # wrong output mode
        result = self.transform.apply(im.im.id, im.im.id)
        return im

##
# (experimental) Fetches the profile for the current display device.
# Returns None if the profile is not known.

def get_display_profile(handle=None):
    import sys
    if sys.platform == "win32":
        import ImageWin
        if isinstance(handle, ImageWin.HDC):
            profile = core.get_display_profile_win32(handle, 1)
        else:
            profile = core.get_display_profile_win32(handle or 0)
    else:
        try:
            get = _imagingcms.get_display_profile
        except AttributeError:
            return None
        else:
            profile = get()
    return ImageCmsProfile(profile)

# --------------------------------------------------------------------.
# pyCMS compatible layer
# --------------------------------------------------------------------.

##
# (pyCMS) Exception class.  This is used for all errors in the pyCMS API.

class PyCMSError(Exception):
    pass

##
# (pyCMS) Applies an ICC transformation to a given image, mapping from
# inputProfile to outputProfile.

def profileToProfile(im, inputProfile, outputProfile, renderingIntent=INTENT_PERCEPTUAL, outputMode=None, inPlace=0, flags=0):
    """
    ImageCms.profileToProfile(im, inputProfile, outputProfile,
        [renderingIntent], [outputMode], [inPlace])

    Returns either None or a new PIL image object, depending on value of
    inPlace (see below).

    im = an open PIL image object (i.e. Image.new(...) or
        Image.open(...), etc.)
    inputProfile = string, as a valid filename path to the ICC input
        profile you wish to use for this image, or a profile object
    outputProfile = string, as a valid filename path to the ICC output
        profile you wish to use for this image, or a profile object
    renderingIntent = integer (0-3) specifying the rendering intent you
        wish to use for the transform
        INTENT_PERCEPTUAL =           0 (DEFAULT) (ImageCms.INTENT_PERCEPTUAL)
        INTENT_RELATIVE_COLORIMETRIC =1 (ImageCms.INTENT_RELATIVE_COLORIMETRIC)
        INTENT_SATURATION =           2 (ImageCms.INTENT_SATURATION)
        INTENT_ABSOLUTE_COLORIMETRIC =3 (ImageCms.INTENT_ABSOLUTE_COLORIMETRIC)

        see the pyCMS documentation for details on rendering intents and
        what they do.
    outputMode = a valid PIL mode for the output image (i.e. "RGB", "CMYK",
        etc.).  Note: if rendering the image "inPlace", outputMode MUST be
        the same mode as the input, or omitted completely.  If omitted, the
        outputMode will be the same as the mode of the input image (im.mode)
    inPlace = BOOL (1 = TRUE, None or 0 = FALSE).  If TRUE, the original
        image is modified in-place, and None is returned.  If FALSE
        (default), a new Image object is returned with the transform
        applied.
    flags = integer (0-...) specifying additional flags

    If the input or output profiles specified are not valid filenames, a
    PyCMSError will be raised.  If inPlace == TRUE and outputMode != im.mode,
    a PyCMSError will be raised.  If an error occurs during application of
    the profiles, a PyCMSError will be raised.  If outputMode is not a mode
    supported by the outputProfile (or by pyCMS), a PyCMSError will be
    raised.

    This function applies an ICC transformation to im from inputProfile's
    color space to outputProfile's color space using the specified rendering
    intent to decide how to handle out-of-gamut colors.

    OutputMode can be used to specify that a color mode conversion is to
    be done using these profiles, but the specified profiles must be able
    to handle that mode.  I.e., if converting im from RGB to CMYK using
    profiles, the input profile must handle RGB data, and the output
    profile must handle CMYK data.

    """

    if outputMode is None:
        outputMode = im.mode

    if type(renderingIntent) != type(1) or not (0 <= renderingIntent <=3):
        raise PyCMSError("renderingIntent must be an integer between 0 and 3")

    if type(flags) != type(1) or not (0 <= flags <= _MAX_FLAG):
        raise PyCMSError("flags must be an integer between 0 and %s" + _MAX_FLAG)

    try:
        if not isinstance(inputProfile, ImageCmsProfile):
            inputProfile = ImageCmsProfile(inputProfile)
        if not isinstance(outputProfile, ImageCmsProfile):
            outputProfile = ImageCmsProfile(outputProfile)
        transform = ImageCmsTransform(
            inputProfile, outputProfile, im.mode, outputMode, renderingIntent, flags=flags
            )
        if inPlace:
            transform.apply_in_place(im)
            imOut = None
        else:
            imOut = transform.apply(im)
    except (IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

    return imOut

##
# (pyCMS) Opens an ICC profile file.

def getOpenProfile(profileFilename):
    """
    ImageCms.getOpenProfile(profileFilename)

    Returns a CmsProfile class object.

    profileFilename = string, as a valid filename path to the ICC profile
        you wish to open, or a file-like object.

    The PyCMSProfile object can be passed back into pyCMS for use in creating
    transforms and such (as in ImageCms.buildTransformFromOpenProfiles()).

    If profileFilename is not a vaild filename for an ICC profile, a
    PyCMSError will be raised.

    """

    try:
        return ImageCmsProfile(profileFilename)
    except (IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

##
# (pyCMS) Builds an ICC transform mapping from the inputProfile to the
# outputProfile.  Use applyTransform to apply the transform to a given
# image.

def buildTransform(inputProfile, outputProfile, inMode, outMode, renderingIntent=INTENT_PERCEPTUAL, flags=0):
    """
    ImageCms.buildTransform(inputProfile, outputProfile, inMode, outMode,
        [renderingIntent])

    Returns a CmsTransform class object.

    inputProfile = string, as a valid filename path to the ICC input
        profile you wish to use for this transform, or a profile object
    outputProfile = string, as a valid filename path to the ICC output
        profile you wish to use for this transform, or a profile object
    inMode = string, as a valid PIL mode that the appropriate profile also
        supports (i.e. "RGB", "RGBA", "CMYK", etc.)
    outMode = string, as a valid PIL mode that the appropriate profile also
        supports (i.e. "RGB", "RGBA", "CMYK", etc.)
    renderingIntent = integer (0-3) specifying the rendering intent you
        wish to use for the transform
        INTENT_PERCEPTUAL =           0 (DEFAULT) (ImageCms.INTENT_PERCEPTUAL)
        INTENT_RELATIVE_COLORIMETRIC =1 (ImageCms.INTENT_RELATIVE_COLORIMETRIC)
        INTENT_SATURATION =           2 (ImageCms.INTENT_SATURATION)
        INTENT_ABSOLUTE_COLORIMETRIC =3 (ImageCms.INTENT_ABSOLUTE_COLORIMETRIC)
        see the pyCMS documentation for details on rendering intents and
        what they do.
    flags = integer (0-...) specifying additional flags

    If the input or output profiles specified are not valid filenames, a
    PyCMSError will be raised.  If an error occurs during creation of the
    transform, a PyCMSError will be raised.

    If inMode or outMode are not a mode supported by the outputProfile (or
    by pyCMS), a PyCMSError will be raised.

    This function builds and returns an ICC transform from the inputProfile
    to the outputProfile using the renderingIntent to determine what to do
    with out-of-gamut colors.  It will ONLY work for converting images that
    are in inMode to images that are in outMode color format (PIL mode,
    i.e. "RGB", "RGBA", "CMYK", etc.).

    Building the transform is a fair part of the overhead in
    ImageCms.profileToProfile(), so if you're planning on converting multiple
    images using the same input/output settings, this can save you time.
    Once you have a transform object, it can be used with
    ImageCms.applyProfile() to convert images without the need to re-compute
    the lookup table for the transform.

    The reason pyCMS returns a class object rather than a handle directly
    to the transform is that it needs to keep track of the PIL input/output
    modes that the transform is meant for.  These attributes are stored in
    the "inMode" and "outMode" attributes of the object (which can be
    manually overridden if you really want to, but I don't know of any
    time that would be of use, or would even work).

    """

    if type(renderingIntent) != type(1) or not (0 <= renderingIntent <=3):
        raise PyCMSError("renderingIntent must be an integer between 0 and 3")

    if type(flags) != type(1) or not (0 <= flags <= _MAX_FLAG):
        raise PyCMSError("flags must be an integer between 0 and %s" + _MAX_FLAG)

    try:
        if not isinstance(inputProfile, ImageCmsProfile):
            inputProfile = ImageCmsProfile(inputProfile)
        if not isinstance(outputProfile, ImageCmsProfile):
            outputProfile = ImageCmsProfile(outputProfile)
        return ImageCmsTransform(inputProfile, outputProfile, inMode, outMode, renderingIntent, flags=flags)
    except (IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

##
# (pyCMS) Builds an ICC transform mapping from the inputProfile to the
# outputProfile, but tries to simulate the result that would be
# obtained on the proofProfile device.

def buildProofTransform(inputProfile, outputProfile, proofProfile, inMode, outMode, renderingIntent=INTENT_PERCEPTUAL, proofRenderingIntent=INTENT_ABSOLUTE_COLORIMETRIC, flags=FLAGS["SOFTPROOFING"]):
    """
    ImageCms.buildProofTransform(inputProfile, outputProfile, proofProfile,
        inMode, outMode, [renderingIntent], [proofRenderingIntent])

    Returns a CmsTransform class object.

    inputProfile = string, as a valid filename path to the ICC input
        profile you wish to use for this transform, or a profile object
    outputProfile = string, as a valid filename path to the ICC output
        (monitor, usually) profile you wish to use for this transform,
        or a profile object
    proofProfile = string, as a valid filename path to the ICC proof
        profile you wish to use for this transform, or a profile object
    inMode = string, as a valid PIL mode that the appropriate profile also
        supports (i.e. "RGB", "RGBA", "CMYK", etc.)
    outMode = string, as a valid PIL mode that the appropriate profile also
        supports (i.e. "RGB", "RGBA", "CMYK", etc.)
    renderingIntent = integer (0-3) specifying the rendering intent you
        wish to use for the input->proof (simulated) transform
        INTENT_PERCEPTUAL =           0 (DEFAULT) (ImageCms.INTENT_PERCEPTUAL)
        INTENT_RELATIVE_COLORIMETRIC =1 (ImageCms.INTENT_RELATIVE_COLORIMETRIC)
        INTENT_SATURATION =           2 (ImageCms.INTENT_SATURATION)
        INTENT_ABSOLUTE_COLORIMETRIC =3 (ImageCms.INTENT_ABSOLUTE_COLORIMETRIC)
        see the pyCMS documentation for details on rendering intents and
        what they do.
    proofRenderingIntent = integer (0-3) specifying the rendering intent
        you wish to use for proof->output transform
        INTENT_PERCEPTUAL =           0 (DEFAULT) (ImageCms.INTENT_PERCEPTUAL)
        INTENT_RELATIVE_COLORIMETRIC =1 (ImageCms.INTENT_RELATIVE_COLORIMETRIC)
        INTENT_SATURATION =           2 (ImageCms.INTENT_SATURATION)
        INTENT_ABSOLUTE_COLORIMETRIC =3 (ImageCms.INTENT_ABSOLUTE_COLORIMETRIC)
        see the pyCMS documentation for details on rendering intents and
        what they do.
    flags = integer (0-...) specifying additional flags

    If the input, output, or proof profiles specified are not valid
    filenames, a PyCMSError will be raised.

    If an error occurs during creation of the transform, a PyCMSError will
    be raised.

    If inMode or outMode are not a mode supported by the outputProfile
    (or by pyCMS), a PyCMSError will be raised.

    This function builds and returns an ICC transform from the inputProfile
    to the outputProfile, but tries to simulate the result that would be
    obtained on the proofProfile device using renderingIntent and
    proofRenderingIntent to determine what to do with out-of-gamut
    colors.  This is known as "soft-proofing".  It will ONLY work for
    converting images that are in inMode to images that are in outMode
    color format (PIL mode, i.e. "RGB", "RGBA", "CMYK", etc.).

    Usage of the resulting transform object is exactly the same as with
    ImageCms.buildTransform().

    Proof profiling is generally used when using an output device to get a
    good idea of what the final printed/displayed image would look like on
    the proofProfile device when it's quicker and easier to use the
    output device for judging color.  Generally, this means that the
    output device is a monitor, or a dye-sub printer (etc.), and the simulated
    device is something more expensive, complicated, or time consuming
    (making it difficult to make a real print for color judgement purposes).

    Soft-proofing basically functions by adjusting the colors on the
    output device to match the colors of the device being simulated. However,
    when the simulated device has a much wider gamut than the output
    device, you may obtain marginal results.

    """

    if type(renderingIntent) != type(1) or not (0 <= renderingIntent <=3):
        raise PyCMSError("renderingIntent must be an integer between 0 and 3")

    if type(flags) != type(1) or not (0 <= flags <= _MAX_FLAG):
        raise PyCMSError("flags must be an integer between 0 and %s" + _MAX_FLAG)

    try:
        if not isinstance(inputProfile, ImageCmsProfile):
            inputProfile = ImageCmsProfile(inputProfile)
        if not isinstance(outputProfile, ImageCmsProfile):
            outputProfile = ImageCmsProfile(outputProfile)
        if not isinstance(proofProfile, ImageCmsProfile):
            proofProfile = ImageCmsProfile(proofProfile)
        return ImageCmsTransform(inputProfile, outputProfile, inMode, outMode, renderingIntent, proofProfile, proofRenderingIntent, flags)
    except (IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

buildTransformFromOpenProfiles = buildTransform
buildProofTransformFromOpenProfiles = buildProofTransform

##
# (pyCMS) Applies a transform to a given image.

def applyTransform(im, transform, inPlace=0):
    """
    ImageCms.applyTransform(im, transform, [inPlace])

    Returns either None, or a new PIL Image object, depending on the value
        of inPlace (see below)

    im = a PIL Image object, and im.mode must be the same as the inMode
        supported by the transform.
    transform = a valid CmsTransform class object
    inPlace = BOOL (1 == TRUE, 0 or None == FALSE).  If TRUE, im is
        modified in place and None is returned, if FALSE, a new Image
        object with the transform applied is returned (and im is not
        changed).  The default is FALSE.

    If im.mode != transform.inMode, a PyCMSError is raised.

    If inPlace == TRUE and transform.inMode != transform.outMode, a
    PyCMSError is raised.

    If im.mode, transfer.inMode, or transfer.outMode is not supported by
    pyCMSdll or the profiles you used for the transform, a PyCMSError is
    raised.

    If an error occurs while the transform is being applied, a PyCMSError
    is raised.

    This function applies a pre-calculated transform (from
    ImageCms.buildTransform() or ImageCms.buildTransformFromOpenProfiles()) to an
    image.  The transform can be used for multiple images, saving
    considerable calcuation time if doing the same conversion multiple times.

    If you want to modify im in-place instead of receiving a new image as
    the return value, set inPlace to TRUE.  This can only be done if
    transform.inMode and transform.outMode are the same, because we can't
    change the mode in-place (the buffer sizes for some modes are
    different).  The  default behavior is to return a new Image object of
    the same dimensions in mode transform.outMode.

    """

    try:
        if inPlace:
            transform.apply_in_place(im)
            imOut = None
        else:
            imOut = transform.apply(im)
    except (TypeError, ValueError), v:
        raise PyCMSError(v)

    return imOut

##
# (pyCMS) Creates a profile.

def createProfile(colorSpace, colorTemp=-1):
    """
    ImageCms.createProfile(colorSpace, [colorTemp])

    Returns a CmsProfile class object

    colorSpace = string, the color space of the profile you wish to create.
        Currently only "LAB", "XYZ", and "sRGB" are supported.
    colorTemp = positive integer for the white point for the profile, in
        degrees Kelvin (i.e. 5000, 6500, 9600, etc.).  The default is for
        D50 illuminant if omitted (5000k).  colorTemp is ONLY applied to
        LAB profiles, and is ignored for XYZ and sRGB.

    If colorSpace not in ["LAB", "XYZ", "sRGB"], a PyCMSError is raised

    If using LAB and colorTemp != a positive integer, a PyCMSError is raised.

    If an error occurs while creating the profile, a PyCMSError is raised.

    Use this function to create common profiles on-the-fly instead of
    having to supply a profile on disk and knowing the path to it.  It
    returns a normal CmsProfile object that can be passed to
    ImageCms.buildTransformFromOpenProfiles() to create a transform to apply
    to images.

    """
    if colorSpace not in ["LAB", "XYZ", "sRGB"]:
        raise PyCMSError("Color space not supported for on-the-fly profile creation (%s)" % colorSpace)

    if colorSpace == "LAB":
        if type(colorTemp) == type(5000.0):
            colorTemp = int(colorTemp + 0.5)
        if type (colorTemp) != type (5000):
            raise PyCMSError("Color temperature must be a positive integer, \"%s\" not valid" % colorTemp)

    try:
        return core.createProfile(colorSpace, colorTemp)
    except (TypeError, ValueError), v:
        raise PyCMSError(v)

##
# (pyCMS) Gets the internal product name for the given profile.

def getProfileName(profile):
    """
    ImageCms.getProfileName(profile)

    Returns a string containing the internal name of the profile as stored
        in an ICC tag.

    profile = EITHER a valid CmsProfile object, OR a string of the
        filename of an ICC profile.

    If profile isn't a valid CmsProfile object or filename to a profile,
    a PyCMSError is raised If an error occurs while trying to obtain the
    name tag, a PyCMSError is raised.

    Use this function to obtain the INTERNAL name of the profile (stored
    in an ICC tag in the profile itself), usually the one used when the
    profile was originally created.  Sometimes this tag also contains
    additional information supplied by the creator.

    """
    try:
        # add an extra newline to preserve pyCMS compatibility
        if not isinstance(profile, ImageCmsProfile):
            profile = ImageCmsProfile(profile)
        return profile.profile.product_name + "\n"
    except (AttributeError, IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

##
# (pyCMS) Gets the internal product information for the given profile.

def getProfileInfo(profile):
    """
    ImageCms.getProfileInfo(profile)

    Returns a string containing the internal profile information stored in
        an ICC tag.

    profile = EITHER a valid CmsProfile object, OR a string of the
        filename of an ICC profile.

    If profile isn't a valid CmsProfile object or filename to a profile,
    a PyCMSError is raised.

    If an error occurs while trying to obtain the info tag, a PyCMSError
    is raised

    Use this function to obtain the information stored in the profile's
    info tag.  This often contains details about the profile, and how it
    was created, as supplied by the creator.

    """
    try:
        if not isinstance(profile, ImageCmsProfile):
            profile = ImageCmsProfile(profile)
        # add an extra newline to preserve pyCMS compatibility
        return profile.product_info + "\n"
    except (AttributeError, IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

##
# (pyCMS) Gets the default intent name for the given profile.

def getDefaultIntent(profile):
    """
    ImageCms.getDefaultIntent(profile)

    Returns integer 0-3 specifying the default rendering intent for this
        profile.
        INTENT_PERCEPTUAL =           0 (DEFAULT) (ImageCms.INTENT_PERCEPTUAL)
        INTENT_RELATIVE_COLORIMETRIC =1 (ImageCms.INTENT_RELATIVE_COLORIMETRIC)
        INTENT_SATURATION =           2 (ImageCms.INTENT_SATURATION)
        INTENT_ABSOLUTE_COLORIMETRIC =3 (ImageCms.INTENT_ABSOLUTE_COLORIMETRIC)
        see the pyCMS documentation for details on rendering intents and
        what they do.

    profile = EITHER a valid CmsProfile object, OR a string of the
        filename of an ICC profile.

    If profile isn't a valid CmsProfile object or filename to a profile,
    a PyCMSError is raised.

    If an error occurs while trying to obtain the default intent, a
    PyCMSError is raised.

    Use this function to determine the default (and usually best optomized)
    rendering intent for this profile.  Most profiles support multiple
    rendering intents, but are intended mostly for one type of conversion.
    If you wish to use a different intent than returned, use
    ImageCms.isIntentSupported() to verify it will work first.
    """
    try:
        if not isinstance(profile, ImageCmsProfile):
            profile = ImageCmsProfile(profile)
        return profile.profile.rendering_intent
    except (AttributeError, IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

##
# (pyCMS) Checks if a given intent is supported.

def isIntentSupported(profile, intent, direction):
    """
    ImageCms.isIntentSupported(profile, intent, direction)

    Returns 1 if the intent/direction are supported, -1 if they are not.

    profile = EITHER a valid CmsProfile object, OR a string of the
        filename of an ICC profile.
    intent = integer (0-3) specifying the rendering intent you wish to use
        with this profile
        INTENT_PERCEPTUAL =           0 (DEFAULT) (ImageCms.INTENT_PERCEPTUAL)
        INTENT_RELATIVE_COLORIMETRIC =1 (ImageCms.INTENT_RELATIVE_COLORIMETRIC)
        INTENT_SATURATION =           2 (ImageCms.INTENT_SATURATION)
        INTENT_ABSOLUTE_COLORIMETRIC =3 (ImageCms.INTENT_ABSOLUTE_COLORIMETRIC)
        see the pyCMS documentation for details on rendering intents and
        what they do.
    direction = integer specifing if the profile is to be used for input,
        output, or proof
        INPUT =               0 (or use ImageCms.DIRECTION_INPUT)
        OUTPUT =              1 (or use ImageCms.DIRECTION_OUTPUT)
        PROOF =               2 (or use ImageCms.DIRECTION_PROOF)

    Use this function to verify that you can use your desired
    renderingIntent with profile, and that profile can be used for the
    input/output/proof profile as you desire.

    Some profiles are created specifically for one "direction", can cannot
    be used for others.  Some profiles can only be used for certain
    rendering intents... so it's best to either verify this before trying
    to create a transform with them (using this function), or catch the
    potential PyCMSError that will occur if they don't support the modes
    you select.

    """
    try:
        if not isinstance(profile, ImageCmsProfile):
            profile = ImageCmsProfile(profile)
        # FIXME: I get different results for the same data w. different
        # compilers.  Bug in LittleCMS or in the binding?
        if profile.profile.is_intent_supported(intent, direction):
            return 1
        else:
            return -1
    except (AttributeError, IOError, TypeError, ValueError), v:
        raise PyCMSError(v)

##
# (pyCMS) Fetches versions.

def versions():
    import sys
    return (
        VERSION, core.littlecms_version, sys.version.split()[0], Image.VERSION
        )

# --------------------------------------------------------------------

if __name__ == "__main__":
    # create a cheap manual from the __doc__ strings for the functions above

    import ImageCms
    import string
    print __doc__

    for f in dir(pyCMS):
        print "="*80
        print "%s" %f

        try:
            exec ("doc = ImageCms.%s.__doc__" %(f))
            if string.find(doc, "pyCMS") >= 0:
                # so we don't get the __doc__ string for imported modules
                print doc
        except AttributeError:
            pass
