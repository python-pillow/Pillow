from tester import *

from PIL import Image
try:
    from PIL import ImageCms
except ImportError:
    skip()

SRGB = "Tests/icc/sRGB.icm"

def test_sanity():

    # basic smoke test.
    # this mostly follows the cms_test outline.

    v = ImageCms.versions() # should return four strings
    assert_equal(v[0], '1.0.0 pil')
    assert_equal(list(map(type, v)), [str, str, str, str])

    # internal version number
    assert_match(ImageCms.core.littlecms_version, "\d+\.\d+$")

    i = ImageCms.profileToProfile(lena(), SRGB, SRGB)
    assert_image(i, "RGB", (128, 128))

    t = ImageCms.buildTransform(SRGB, SRGB, "RGB", "RGB")
    i = ImageCms.applyTransform(lena(), t)
    assert_image(i, "RGB", (128, 128))

    p = ImageCms.createProfile("sRGB")
    o = ImageCms.getOpenProfile(SRGB)
    t = ImageCms.buildTransformFromOpenProfiles(p, o, "RGB", "RGB")
    i = ImageCms.applyTransform(lena(), t)
    assert_image(i, "RGB", (128, 128))

    t = ImageCms.buildProofTransform(SRGB, SRGB, SRGB, "RGB", "RGB")
    assert_equal(t.inputMode, "RGB")
    assert_equal(t.outputMode, "RGB")
    i = ImageCms.applyTransform(lena(), t)
    assert_image(i, "RGB", (128, 128))

    # test PointTransform convenience API
    im = lena().point(t)

def test_name():
    # get profile information for file
    assert_equal(ImageCms.getProfileName(SRGB).strip(),
                 'IEC 61966-2.1 Default RGB colour space - sRGB')
def x_test_info():
    assert_equal(ImageCms.getProfileInfo(SRGB).splitlines(),
                 ['sRGB IEC61966-2.1', '',
                  'Copyright (c) 1998 Hewlett-Packard Company', '',
                  'WhitePoint : D65 (daylight)', '',
                  'Tests/icc/sRGB.icm'])

def test_intent():
    assert_equal(ImageCms.getDefaultIntent(SRGB), 0)
    assert_equal(ImageCms.isIntentSupported(
            SRGB, ImageCms.INTENT_ABSOLUTE_COLORIMETRIC,
            ImageCms.DIRECTION_INPUT), 1)

def test_profile_object():
    # same, using profile object
    p = ImageCms.createProfile("sRGB")
#    assert_equal(ImageCms.getProfileName(p).strip(),
#                 'sRGB built-in - (lcms internal)')
#    assert_equal(ImageCms.getProfileInfo(p).splitlines(),
#                 ['sRGB built-in', '', 'WhitePoint : D65 (daylight)', '', ''])
    assert_equal(ImageCms.getDefaultIntent(p), 0)
    assert_equal(ImageCms.isIntentSupported(
            p, ImageCms.INTENT_ABSOLUTE_COLORIMETRIC,
            ImageCms.DIRECTION_INPUT), 1)

def test_extensions():
    # extensions
    i = Image.open("Tests/images/rgb.jpg")
    p = ImageCms.getOpenProfile(BytesIO(i.info["icc_profile"]))
    assert_equal(ImageCms.getProfileName(p).strip(),
                 'IEC 61966-2.1 Default RGB colour space - sRGB')

def test_exceptions():
    # the procedural pyCMS API uses PyCMSError for all sorts of errors
    assert_exception(ImageCms.PyCMSError, lambda: ImageCms.profileToProfile(lena(), "foo", "bar"))
    assert_exception(ImageCms.PyCMSError, lambda: ImageCms.buildTransform("foo", "bar", "RGB", "RGB"))
    assert_exception(ImageCms.PyCMSError, lambda: ImageCms.getProfileName(None))
    assert_exception(ImageCms.PyCMSError, lambda: ImageCms.isIntentSupported(SRGB, None, None))


def test_display_profile():
    # try fetching the profile for the current display device
    assert_no_exception(lambda: ImageCms.get_display_profile())


def test_lab_color_profile():
    pLab = ImageCms.createProfile("LAB", 5000)
    pLab = ImageCms.createProfile("LAB", 6500)

def test_simple_lab():
    i = Image.new('RGB', (10,10), (128,128,128))

    pLab = ImageCms.createProfile("LAB")    
    t = ImageCms.buildTransform(SRGB, pLab, "RGB", "LAB")

    i_lab = ImageCms.applyTransform(i, t)


    assert_equal(i_lab.mode, 'LAB')

    k = i_lab.getpixel((0,0))
    assert_equal(k, (137,128,128)) # not a linear luminance map. so L != 128

    L  = i_lab.getdata(0)
    a = i_lab.getdata(1)
    b = i_lab.getdata(2)

    assert_equal(list(L), [137]*100)
    assert_equal(list(a), [128]*100)
    assert_equal(list(b), [128]*100)

    
def test_lab_color():
    pLab = ImageCms.createProfile("LAB")    
    t = ImageCms.buildTransform(SRGB, pLab, "RGB", "LAB")
    # need to add a type mapping for some PIL type to TYPE_Lab_8 in findLCMSType,
    # and have that mapping work back to a PIL mode. (likely RGB)
    i = ImageCms.applyTransform(lena(), t)
    assert_image(i, "LAB", (128, 128))
    
    # i.save('temp.lab.tif')  # visually verified vs PS. 

    target = Image.open('Tests/images/lena.Lab.tif')

    assert_image_similar(i, target, 30)

def test_lab_srgb():
    pLab = ImageCms.createProfile("LAB")    
    t = ImageCms.buildTransform(pLab, SRGB, "LAB", "RGB")

    img = Image.open('Tests/images/lena.Lab.tif')

    img_srgb = ImageCms.applyTransform(img, t)

    # img_srgb.save('temp.srgb.tif') # visually verified vs ps. 
    
    assert_image_similar(lena(), img_srgb, 30)

def test_lab_roundtrip():
    # check to see if we're at least internally consistent. 
    pLab = ImageCms.createProfile("LAB")    
    t = ImageCms.buildTransform(SRGB, pLab, "RGB", "LAB")

    t2 = ImageCms.buildTransform(pLab, SRGB, "LAB", "RGB")

    i = ImageCms.applyTransform(lena(), t)
    out = ImageCms.applyTransform(i, t2)

    assert_image_similar(lena(), out, 2)


