from PIL import Image

from .helper import PillowTestCase

try:
    from PIL import _webp

    HAVE_WEBP = True
except ImportError:
    HAVE_WEBP = False


class TestFileWebpAnimation(PillowTestCase):
    def setUp(self):
        if not HAVE_WEBP:
            self.skipTest("WebP support not installed")
            return

        if not _webp.HAVE_WEBPANIM:
            self.skipTest(
                "WebP library does not contain animation support, "
                "not testing animation"
            )

    def test_n_frames(self):
        """
        Ensure that WebP format sets n_frames and is_animated
        attributes correctly.
        """

        with Image.open("Tests/images/hopper.webp") as im:
            self.assertEqual(im.n_frames, 1)
            self.assertFalse(im.is_animated)

        with Image.open("Tests/images/iss634.webp") as im:
            self.assertEqual(im.n_frames, 42)
            self.assertTrue(im.is_animated)

    def test_write_animation_L(self):
        """
        Convert an animated GIF to animated WebP, then compare the
        frame count, and first and last frames to ensure they're
        visually similar.
        """

        with Image.open("Tests/images/iss634.gif") as orig:
            self.assertGreater(orig.n_frames, 1)

            temp_file = self.tempfile("temp.webp")
            orig.save(temp_file, save_all=True)
            with Image.open(temp_file) as im:
                self.assertEqual(im.n_frames, orig.n_frames)

                # Compare first and last frames to the original animated GIF
                orig.load()
                im.load()
                self.assert_image_similar(im, orig.convert("RGBA"), 25.0)
                orig.seek(orig.n_frames - 1)
                im.seek(im.n_frames - 1)
                orig.load()
                im.load()
                self.assert_image_similar(im, orig.convert("RGBA"), 25.0)

    def test_write_animation_RGB(self):
        """
        Write an animated WebP from RGB frames, and ensure the frames
        are visually similar to the originals.
        """

        def check(temp_file):
            with Image.open(temp_file) as im:
                self.assertEqual(im.n_frames, 2)

                # Compare first frame to original
                im.load()
                self.assert_image_equal(im, frame1.convert("RGBA"))

                # Compare second frame to original
                im.seek(1)
                im.load()
                self.assert_image_equal(im, frame2.convert("RGBA"))

        with Image.open("Tests/images/anim_frame1.webp") as frame1:
            with Image.open("Tests/images/anim_frame2.webp") as frame2:
                temp_file1 = self.tempfile("temp.webp")
                frame1.copy().save(
                    temp_file1, save_all=True, append_images=[frame2], lossless=True
                )
                check(temp_file1)

                # Tests appending using a generator
                def imGenerator(ims):
                    yield from ims

                temp_file2 = self.tempfile("temp_generator.webp")
                frame1.copy().save(
                    temp_file2,
                    save_all=True,
                    append_images=imGenerator([frame2]),
                    lossless=True,
                )
                check(temp_file2)

    def test_timestamp_and_duration(self):
        """
        Try passing a list of durations, and make sure the encoded
        timestamps and durations are correct.
        """

        durations = [0, 10, 20, 30, 40]
        temp_file = self.tempfile("temp.webp")
        with Image.open("Tests/images/anim_frame1.webp") as frame1:
            with Image.open("Tests/images/anim_frame2.webp") as frame2:
                frame1.save(
                    temp_file,
                    save_all=True,
                    append_images=[frame2, frame1, frame2, frame1],
                    duration=durations,
                )

        with Image.open(temp_file) as im:
            self.assertEqual(im.n_frames, 5)
            self.assertTrue(im.is_animated)

            # Check that timestamps and durations match original values specified
            ts = 0
            for frame in range(im.n_frames):
                im.seek(frame)
                im.load()
                self.assertEqual(im.info["duration"], durations[frame])
                self.assertEqual(im.info["timestamp"], ts)
                ts += durations[frame]

    def test_seeking(self):
        """
        Create an animated WebP file, and then try seeking through
        frames in reverse-order, verifying the timestamps and durations
        are correct.
        """

        dur = 33
        temp_file = self.tempfile("temp.webp")
        with Image.open("Tests/images/anim_frame1.webp") as frame1:
            with Image.open("Tests/images/anim_frame2.webp") as frame2:
                frame1.save(
                    temp_file,
                    save_all=True,
                    append_images=[frame2, frame1, frame2, frame1],
                    duration=dur,
                )

        with Image.open(temp_file) as im:
            self.assertEqual(im.n_frames, 5)
            self.assertTrue(im.is_animated)

            # Traverse frames in reverse, checking timestamps and durations
            ts = dur * (im.n_frames - 1)
            for frame in reversed(range(im.n_frames)):
                im.seek(frame)
                im.load()
                self.assertEqual(im.info["duration"], dur)
                self.assertEqual(im.info["timestamp"], ts)
                ts -= dur
