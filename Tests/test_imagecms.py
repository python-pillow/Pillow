from helper import unittest, PillowTestCase, hopper

from PIL import Image

from io import BytesIO
import os

try:
    from PIL import ImageCms
    from PIL.ImageCms import ImageCmsProfile
    ImageCms.core.profile_open
except ImportError as v:
    # Skipped via setUp()
    pass


SRGB = "Tests/icc/sRGB_IEC61966-2-1_black_scaled.icc"
HAVE_PROFILE = os.path.exists(SRGB)


class TestImageCms(PillowTestCase):

    def setUp(self):
        try:
            from PIL import ImageCms
            # need to hit getattr to trigger the delayed import error
            ImageCms.core.profile_open
        except ImportError as v:
            self.skipTest(v)

    def skip_missing(self):
        if not HAVE_PROFILE:
            self.skipTest("SRGB profile not available")

    def test_sanity(self):

        # basic smoke test.
        # this mostly follows the cms_test outline.

        v = ImageCms.versions()  # should return four strings
        self.assertEqual(v[0], '1.0.0 pil')
        self.assertEqual(list(map(type, v)), [str, str, str, str])

        # internal version number
        self.assertRegexpMatches(ImageCms.core.littlecms_version, "\d+\.\d+$")

        self.skip_missing()
        i = ImageCms.profileToProfile(hopper(), SRGB, SRGB)
        self.assert_image(i, "RGB", (128, 128))

        i = hopper()
        ImageCms.profileToProfile(i, SRGB, SRGB, inPlace=True)
        self.assert_image(i, "RGB", (128, 128))

        t = ImageCms.buildTransform(SRGB, SRGB, "RGB", "RGB")
        i = ImageCms.applyTransform(hopper(), t)
        self.assert_image(i, "RGB", (128, 128))

        i = hopper()
        t = ImageCms.buildTransform(SRGB, SRGB, "RGB", "RGB")
        ImageCms.applyTransform(hopper(), t, inPlace=True)
        self.assert_image(i, "RGB", (128, 128))

        p = ImageCms.createProfile("sRGB")
        o = ImageCms.getOpenProfile(SRGB)
        t = ImageCms.buildTransformFromOpenProfiles(p, o, "RGB", "RGB")
        i = ImageCms.applyTransform(hopper(), t)
        self.assert_image(i, "RGB", (128, 128))

        t = ImageCms.buildProofTransform(SRGB, SRGB, SRGB, "RGB", "RGB")
        self.assertEqual(t.inputMode, "RGB")
        self.assertEqual(t.outputMode, "RGB")
        i = ImageCms.applyTransform(hopper(), t)
        self.assert_image(i, "RGB", (128, 128))

        # test PointTransform convenience API
        hopper().point(t)

    def test_name(self):
        self.skip_missing()
        # get profile information for file
        self.assertEqual(
            ImageCms.getProfileName(SRGB).strip(),
            'IEC 61966-2-1 Default RGB Colour Space - sRGB')

    def test_info(self):
        self.skip_missing()
        self.assertEqual(
            ImageCms.getProfileInfo(SRGB).splitlines(), [
                'sRGB IEC61966-2-1 black scaled', '',
                'Copyright International Color Consortium, 2009', ''])

    def test_copyright(self):
        self.skip_missing()
        self.assertEqual(
            ImageCms.getProfileCopyright(SRGB).strip(),
            'Copyright International Color Consortium, 2009')

    def test_manufacturer(self):
        self.skip_missing()
        self.assertEqual(
            ImageCms.getProfileManufacturer(SRGB).strip(),
            '')

    def test_model(self):
        self.skip_missing()
        self.assertEqual(
            ImageCms.getProfileModel(SRGB).strip(),
            'IEC 61966-2-1 Default RGB Colour Space - sRGB')

    def test_description(self):
        self.skip_missing()
        self.assertEqual(
            ImageCms.getProfileDescription(SRGB).strip(),
            'sRGB IEC61966-2-1 black scaled')

    def test_intent(self):
        self.skip_missing()
        self.assertEqual(ImageCms.getDefaultIntent(SRGB), 0)
        self.assertEqual(ImageCms.isIntentSupported(
            SRGB, ImageCms.INTENT_ABSOLUTE_COLORIMETRIC,
            ImageCms.DIRECTION_INPUT), 1)

    def test_profile_object(self):
        # same, using profile object
        p = ImageCms.createProfile("sRGB")
    #    self.assertEqual(ImageCms.getProfileName(p).strip(),
    #                 'sRGB built-in - (lcms internal)')
    #    self.assertEqual(ImageCms.getProfileInfo(p).splitlines(),
    #             ['sRGB built-in', '', 'WhitePoint : D65 (daylight)', '', ''])
        self.assertEqual(ImageCms.getDefaultIntent(p), 0)
        self.assertEqual(ImageCms.isIntentSupported(
            p, ImageCms.INTENT_ABSOLUTE_COLORIMETRIC,
            ImageCms.DIRECTION_INPUT), 1)

    def test_extensions(self):
        # extensions

        i = Image.open("Tests/images/rgb.jpg")
        p = ImageCms.getOpenProfile(BytesIO(i.info["icc_profile"]))
        self.assertEqual(
            ImageCms.getProfileName(p).strip(),
            'IEC 61966-2.1 Default RGB colour space - sRGB')

    def test_exceptions(self):
        # the procedural pyCMS API uses PyCMSError for all sorts of errors
        self.assertRaises(
            ImageCms.PyCMSError,
            lambda: ImageCms.profileToProfile(hopper(), "foo", "bar"))
        self.assertRaises(
            ImageCms.PyCMSError,
            lambda: ImageCms.buildTransform("foo", "bar", "RGB", "RGB"))
        self.assertRaises(
            ImageCms.PyCMSError,
            lambda: ImageCms.getProfileName(None))
        self.skip_missing()
        self.assertRaises(
            ImageCms.PyCMSError,
            lambda: ImageCms.isIntentSupported(SRGB, None, None))

    def test_display_profile(self):
        # try fetching the profile for the current display device
        ImageCms.get_display_profile()

    def test_lab_color_profile(self):
        ImageCms.createProfile("LAB", 5000)
        ImageCms.createProfile("LAB", 6500)

    def test_simple_lab(self):
        i = Image.new('RGB', (10, 10), (128, 128, 128))

        psRGB = ImageCms.createProfile("sRGB")
        pLab = ImageCms.createProfile("LAB")
        t = ImageCms.buildTransform(psRGB, pLab, "RGB", "LAB")

        i_lab = ImageCms.applyTransform(i, t)

        self.assertEqual(i_lab.mode, 'LAB')

        k = i_lab.getpixel((0, 0))
        # not a linear luminance map. so L != 128:
        self.assertEqual(k, (137, 128, 128))

        l = i_lab.getdata(0)
        a = i_lab.getdata(1)
        b = i_lab.getdata(2)

        self.assertEqual(list(l), [137] * 100)
        self.assertEqual(list(a), [128] * 100)
        self.assertEqual(list(b), [128] * 100)

    def test_lab_color(self):
        psRGB = ImageCms.createProfile("sRGB")
        pLab = ImageCms.createProfile("LAB")
        t = ImageCms.buildTransform(psRGB, pLab, "RGB", "LAB")

        # Need to add a type mapping for some PIL type to TYPE_Lab_8 in
        # findLCMSType, and have that mapping work back to a PIL mode
        # (likely RGB).
        i = ImageCms.applyTransform(hopper(), t)
        self.assert_image(i, "LAB", (128, 128))

        # i.save('temp.lab.tif')  # visually verified vs PS.

        target = Image.open('Tests/images/hopper.Lab.tif')

        self.assert_image_similar(i, target, 30)

    def test_lab_srgb(self):
        psRGB = ImageCms.createProfile("sRGB")
        pLab = ImageCms.createProfile("LAB")
        t = ImageCms.buildTransform(pLab, psRGB, "LAB", "RGB")

        img = Image.open('Tests/images/hopper.Lab.tif')

        img_srgb = ImageCms.applyTransform(img, t)

        # img_srgb.save('temp.srgb.tif') # visually verified vs ps.

        self.assert_image_similar(hopper(), img_srgb, 30)
        self.assertTrue(img_srgb.info['icc_profile'])

        profile = ImageCmsProfile(BytesIO(img_srgb.info['icc_profile']))
        self.assertTrue('sRGB' in ImageCms.getProfileDescription(profile))

    def test_lab_roundtrip(self):
        # check to see if we're at least internally consistent.
        psRGB = ImageCms.createProfile("sRGB")
        pLab = ImageCms.createProfile("LAB")
        t = ImageCms.buildTransform(psRGB, pLab, "RGB", "LAB")

        t2 = ImageCms.buildTransform(pLab, psRGB, "LAB", "RGB")

        i = ImageCms.applyTransform(hopper(), t)

        self.assertEqual(i.info['icc_profile'],
                         ImageCmsProfile(pLab).tobytes())

        out = ImageCms.applyTransform(i, t2)

        self.assert_image_similar(hopper(), out, 2)

    def test_profile_tobytes(self):
        i = Image.open("Tests/images/rgb.jpg")
        p = ImageCms.getOpenProfile(BytesIO(i.info["icc_profile"]))

        p2 = ImageCms.getOpenProfile(BytesIO(p.tobytes()))

        # not the same bytes as the original icc_profile,
        # but it does roundtrip
        self.assertEqual(p.tobytes(), p2.tobytes())
        self.assertEqual(ImageCms.getProfileName(p),
                         ImageCms.getProfileName(p2))
        self.assertEqual(ImageCms.getProfileDescription(p),
                         ImageCms.getProfileDescription(p2))

if __name__ == '__main__':
    unittest.main()

# End of file
