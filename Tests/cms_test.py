# PyCMSTests.py
# Examples of how to use pyCMS, as well as tests to verify it works properly
# By Kevin Cazabon (kevin@cazabon.com)

# Imports
import os
from PIL import Image
from PIL import ImageCms

# import PyCMSError separately so we can catch it
PyCMSError = ImageCms.PyCMSError

#######################################################################
# Configuration:
#######################################################################
# set this to the image you want to test with
IMAGE = "c:\\temp\\test.tif"

# set this to where you want to save the output images
OUTPUTDIR = "c:\\temp\\"

# set these to two different ICC profiles, one for input, one for output
# set the corresponding mode to the proper PIL mode for that profile
INPUT_PROFILE = "c:\\temp\\profiles\\sRGB.icm"
INMODE = "RGB"

OUTPUT_PROFILE = "c:\\temp\\profiles\\genericRGB.icm"
OUTMODE = "RGB"

PROOF_PROFILE = "c:\\temp\\profiles\\monitor.icm"

# set to True to show() images, False to save them into OUTPUT_DIRECTORY
SHOW = False

# Tests you can enable/disable
TEST_error_catching                 = True
TEST_profileToProfile               = True
TEST_profileToProfile_inPlace       = True
TEST_buildTransform                 = True
TEST_buildTransformFromOpenProfiles = True
TEST_buildProofTransform            = True
TEST_getProfileInfo                 = True
TEST_misc                           = False

#######################################################################
# helper functions
#######################################################################
def outputImage(im, funcName = None):
    # save or display the image, depending on value of SHOW_IMAGES
    if SHOW:
        im.show()
    else:
        im.save(os.path.join(OUTPUTDIR, "%s.tif" %funcName))


#######################################################################
# The tests themselves
#######################################################################

if TEST_error_catching:
    im = Image.open(IMAGE)
    try:
        #neither of these proifles exists (unless you make them), so we should
        # get an error
        imOut = ImageCms.profileToProfile(im, "missingProfile.icm", "cmyk.icm")

    except PyCMSError as reason:
        print("We caught a PyCMSError: %s\n\n" %reason)

    print("error catching test completed successfully (if you see the message \
    above that we caught the error).")

if TEST_profileToProfile:
    # open the image file using the standard PIL function Image.open()
    im = Image.open(IMAGE)

    # send the image, input/output profiles, and rendering intent to
    # ImageCms.profileToProfile()
    imOut = ImageCms.profileToProfile(im, INPUT_PROFILE, OUTPUT_PROFILE, \
                outputMode = OUTMODE)

    # now that the image is converted, save or display it
    outputImage(imOut, "profileToProfile")

    print("profileToProfile test completed successfully.")

if TEST_profileToProfile_inPlace:
    # we'll do the same test as profileToProfile, but modify im in place
    # instead of getting a new image returned to us
    im = Image.open(IMAGE)

    # send the image to ImageCms.profileToProfile(), specifying inPlace = True
    result = ImageCms.profileToProfile(im, INPUT_PROFILE, OUTPUT_PROFILE, \
                outputMode = OUTMODE, inPlace = True)

    # now that the image is converted, save or display it
    if result is None:
        # this is the normal result when modifying in-place
        outputImage(im, "profileToProfile_inPlace")
    else:
        # something failed...
        print("profileToProfile in-place failed: %s" %result)

    print("profileToProfile in-place test completed successfully.")

if TEST_buildTransform:
    # make a transform using the input and output profile path strings
    transform = ImageCms.buildTransform(INPUT_PROFILE, OUTPUT_PROFILE, INMODE, \
                OUTMODE)

    # now, use the trnsform to convert a couple images
    im = Image.open(IMAGE)

    # transform im normally
    im2 = ImageCms.applyTransform(im, transform)
    outputImage(im2, "buildTransform")

    # then transform it again using the same transform, this time in-place.
    result = ImageCms.applyTransform(im, transform, inPlace = True)
    outputImage(im, "buildTransform_inPlace")

    print("buildTransform test completed successfully.")

    # and, to clean up a bit, delete the transform
    # this should call the C destructor for the transform structure.
    # Python should also do this automatically when it goes out of scope.
    del(transform)

if TEST_buildTransformFromOpenProfiles:
    # we'll actually test a couple profile open/creation functions here too

    # first, get a handle to an input profile, in this case we'll create
    # an sRGB profile on the fly:
    inputProfile = ImageCms.createProfile("sRGB")

    # then, get a handle to the output profile
    outputProfile = ImageCms.getOpenProfile(OUTPUT_PROFILE)

    # make a transform from these
    transform = ImageCms.buildTransformFromOpenProfiles(inputProfile, \
                outputProfile, INMODE, OUTMODE)

    # now, use the trnsform to convert a couple images
    im = Image.open(IMAGE)

    # transform im normally
    im2 = ImageCms.applyTransform(im, transform)
    outputImage(im2, "buildTransformFromOpenProfiles")

    # then do it again using the same transform, this time in-place.
    result = ImageCms.applyTransform(im, transform, inPlace = True)
    outputImage(im, "buildTransformFromOpenProfiles_inPlace")

    print("buildTransformFromOpenProfiles test completed successfully.")

    # and, to clean up a bit, delete the transform
    # this should call the C destructor for the each item.
    # Python should also do this automatically when it goes out of scope.
    del(inputProfile)
    del(outputProfile)
    del(transform)

if TEST_buildProofTransform:
    # make a transform using the input and output and proof profile path
    # strings
    # images converted with this transform will simulate the appearance
    # of the output device while actually being displayed/proofed on the
    # proof device.  This usually means a monitor, but can also mean
    # other proof-printers like dye-sub, etc.
    transform = ImageCms.buildProofTransform(INPUT_PROFILE, OUTPUT_PROFILE, \
                PROOF_PROFILE, INMODE, OUTMODE)

    # now, use the trnsform to convert a couple images
    im = Image.open(IMAGE)

    # transform im normally
    im2 = ImageCms.applyTransform(im, transform)
    outputImage(im2, "buildProofTransform")

    # then transform it again using the same transform, this time in-place.
    result = ImageCms.applyTransform(im, transform, inPlace = True)
    outputImage(im, "buildProofTransform_inPlace")

    print("buildProofTransform test completed successfully.")

    # and, to clean up a bit, delete the transform
    # this should call the C destructor for the transform structure.
    # Python should also do this automatically when it goes out of scope.
    del(transform)

if TEST_getProfileInfo:
    # get a profile handle
    profile = ImageCms.getOpenProfile(INPUT_PROFILE)

    # lets print some info about our input profile:
    print("Profile name (retrieved from profile string path name): %s" %ImageCms.getProfileName(INPUT_PROFILE))

    # or, you could do the same thing using a profile handle as the arg
    print("Profile name (retrieved from profile handle): %s" %ImageCms.getProfileName(profile))

    # now lets get the embedded "info" tag contents
    # once again, you can use a path to a profile, or a profile handle
    print("Profile info (retrieved from profile handle): %s" %ImageCms.getProfileInfo(profile))

    # and what's the default intent of this profile?
    print("The default intent is (this will be an integer): %d" %(ImageCms.getDefaultIntent(profile)))

    # Hmmmm... but does this profile support INTENT_ABSOLUTE_COLORIMETRIC?
    print("Does it support INTENT_ABSOLUTE_COLORIMETRIC?: (1 is yes, -1 is no): %s" \
            %ImageCms.isIntentSupported(profile, ImageCms.INTENT_ABSOLUTE_COLORIMETRIC, \
            ImageCms.DIRECTION_INPUT))

    print("getProfileInfo test completed successfully.")

if TEST_misc:
    # test the versions, about, and copyright functions
    print("Versions: %s" %str(ImageCms.versions()))
    print("About:\n\n%s" %ImageCms.about())
    print("Copyright:\n\n%s" %ImageCms.copyright())

    print("misc test completed successfully.")

