import unittest
from io import BytesIO

from PIL import Image

from .helper import PillowTestCase, is_pypy

test_files = ["Tests/images/sugarshack.mpo", "Tests/images/frozenpond.mpo"]


class TestFileMpo(PillowTestCase):
    def setUp(self):
        codecs = dir(Image.core)
        if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
            self.skipTest("jpeg support not available")

    def frame_roundtrip(self, im, **options):
        # Note that for now, there is no MPO saving functionality
        out = BytesIO()
        im.save(out, "MPO", **options)
        test_bytes = out.tell()
        out.seek(0)
        im = Image.open(out)
        im.bytes = test_bytes  # for testing only
        return im

    def test_sanity(self):
        for test_file in test_files:
            with Image.open(test_file) as im:
                im.load()
                self.assertEqual(im.mode, "RGB")
                self.assertEqual(im.size, (640, 480))
                self.assertEqual(im.format, "MPO")

    @unittest.skipIf(is_pypy(), "Requires CPython")
    def test_unclosed_file(self):
        def open():
            im = Image.open(test_files[0])
            im.load()

        self.assert_warning(ResourceWarning, open)

    def test_closed_file(self):
        def open():
            im = Image.open(test_files[0])
            im.load()
            im.close()

        self.assert_warning(None, open)

    def test_context_manager(self):
        def open():
            with Image.open(test_files[0]) as im:
                im.load()

        self.assert_warning(None, open)

    def test_app(self):
        for test_file in test_files:
            # Test APP/COM reader (@PIL135)
            with Image.open(test_file) as im:
                self.assertEqual(im.applist[0][0], "APP1")
                self.assertEqual(im.applist[1][0], "APP2")
                self.assertEqual(
                    im.applist[1][1][:16],
                    b"MPF\x00MM\x00*\x00\x00\x00\x08\x00\x03\xb0\x00",
                )
                self.assertEqual(len(im.applist), 2)

    def test_exif(self):
        for test_file in test_files:
            with Image.open(test_file) as im:
                info = im._getexif()
                self.assertEqual(info[272], "Nintendo 3DS")
                self.assertEqual(info[296], 2)
                self.assertEqual(info[34665], 188)

    def test_frame_size(self):
        # This image has been hexedited to contain a different size
        # in the EXIF data of the second frame
        with Image.open("Tests/images/sugarshack_frame_size.mpo") as im:
            self.assertEqual(im.size, (640, 480))

            im.seek(1)
            self.assertEqual(im.size, (680, 480))

    def test_parallax(self):
        # Nintendo
        with Image.open("Tests/images/sugarshack.mpo") as im:
            exif = im.getexif()
            self.assertEqual(
                exif.get_ifd(0x927C)[0x1101]["Parallax"], -44.798187255859375
            )

        # Fujifilm
        with Image.open("Tests/images/fujifilm.mpo") as im:
            im.seek(1)
            exif = im.getexif()
            self.assertEqual(exif.get_ifd(0x927C)[0xB211], -3.125)

    def test_mp(self):
        for test_file in test_files:
            with Image.open(test_file) as im:
                mpinfo = im._getmp()
                self.assertEqual(mpinfo[45056], b"0100")
                self.assertEqual(mpinfo[45057], 2)

    def test_mp_offset(self):
        # This image has been manually hexedited to have an IFD offset of 10
        # in APP2 data, in contrast to normal 8
        with Image.open("Tests/images/sugarshack_ifd_offset.mpo") as im:
            mpinfo = im._getmp()
            self.assertEqual(mpinfo[45056], b"0100")
            self.assertEqual(mpinfo[45057], 2)

    def test_mp_no_data(self):
        # This image has been manually hexedited to have the second frame
        # beyond the end of the file
        with Image.open("Tests/images/sugarshack_no_data.mpo") as im:
            with self.assertRaises(ValueError):
                im.seek(1)

    def test_mp_attribute(self):
        for test_file in test_files:
            with Image.open(test_file) as im:
                mpinfo = im._getmp()
            frameNumber = 0
            for mpentry in mpinfo[45058]:
                mpattr = mpentry["Attribute"]
                if frameNumber:
                    self.assertFalse(mpattr["RepresentativeImageFlag"])
                else:
                    self.assertTrue(mpattr["RepresentativeImageFlag"])
                self.assertFalse(mpattr["DependentParentImageFlag"])
                self.assertFalse(mpattr["DependentChildImageFlag"])
                self.assertEqual(mpattr["ImageDataFormat"], "JPEG")
                self.assertEqual(mpattr["MPType"], "Multi-Frame Image: (Disparity)")
                self.assertEqual(mpattr["Reserved"], 0)
                frameNumber += 1

    def test_seek(self):
        for test_file in test_files:
            with Image.open(test_file) as im:
                self.assertEqual(im.tell(), 0)
                # prior to first image raises an error, both blatant and borderline
                self.assertRaises(EOFError, im.seek, -1)
                self.assertRaises(EOFError, im.seek, -523)
                # after the final image raises an error,
                # both blatant and borderline
                self.assertRaises(EOFError, im.seek, 2)
                self.assertRaises(EOFError, im.seek, 523)
                # bad calls shouldn't change the frame
                self.assertEqual(im.tell(), 0)
                # this one will work
                im.seek(1)
                self.assertEqual(im.tell(), 1)
                # and this one, too
                im.seek(0)
                self.assertEqual(im.tell(), 0)

    def test_n_frames(self):
        with Image.open("Tests/images/sugarshack.mpo") as im:
            self.assertEqual(im.n_frames, 2)
            self.assertTrue(im.is_animated)

    def test_eoferror(self):
        with Image.open("Tests/images/sugarshack.mpo") as im:
            n_frames = im.n_frames

            # Test seeking past the last frame
            self.assertRaises(EOFError, im.seek, n_frames)
            self.assertLess(im.tell(), n_frames)

            # Test that seeking to the last frame does not raise an error
            im.seek(n_frames - 1)

    def test_image_grab(self):
        for test_file in test_files:
            with Image.open(test_file) as im:
                self.assertEqual(im.tell(), 0)
                im0 = im.tobytes()
                im.seek(1)
                self.assertEqual(im.tell(), 1)
                im1 = im.tobytes()
                im.seek(0)
                self.assertEqual(im.tell(), 0)
                im02 = im.tobytes()
                self.assertEqual(im0, im02)
                self.assertNotEqual(im0, im1)

    def test_save(self):
        # Note that only individual frames can be saved at present
        for test_file in test_files:
            with Image.open(test_file) as im:
                self.assertEqual(im.tell(), 0)
                jpg0 = self.frame_roundtrip(im)
                self.assert_image_similar(im, jpg0, 30)
                im.seek(1)
                self.assertEqual(im.tell(), 1)
                jpg1 = self.frame_roundtrip(im)
                self.assert_image_similar(im, jpg1, 30)
