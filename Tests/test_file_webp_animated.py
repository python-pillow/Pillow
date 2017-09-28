from helper import unittest, PillowTestCase, hopper

from PIL import Image

try:
    from PIL import _webp
except ImportError:
    pass
    # Skip in setUp()


class TestFileWebpAnimation(PillowTestCase):

    def setUp(self):
        try:
            from PIL import _webp
        except ImportError:
            self.skipTest('WebP support not installed')

        if not _webp.HAVE_WEBPANIM:
            self.skipTest("WebP library does not contain animation support, "
                          "not testing animation")

    def test_n_frames(self):
        """
        Ensure that webp format sets n_frames and is_animated
        attributes correctly.
        """

        im = Image.open("Tests/images/hopper.webp")
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

        im = Image.open("Tests/images/iss634.webp")
        self.assertEqual(im.n_frames, 42)
        self.assertTrue(im.is_animated)

    def test_write_animation(self):
        """
        Convert an animated GIF to animated WebP, then compare the
        frame count, and first and last frames to ensure they're
        visually similar.
        """

        orig = Image.open("Tests/images/iss634.gif")
        self.assertGreater(orig.n_frames, 1)

        temp_file = self.tempfile("temp.webp")
        orig.save(temp_file, save_all=True)
        im = Image.open(temp_file)
        self.assertEqual(im.n_frames, orig.n_frames)

        # Compare first and last frames to the original animated GIF
        orig.load()
        im.load()
        self.assert_image_similar(im, orig.convert("RGBA"), 25.0)
        orig.seek(orig.n_frames-1)
        im.seek(im.n_frames-1)
        orig.load()
        im.load()
        self.assert_image_similar(im, orig.convert("RGBA"), 25.0)

    def test_timestamp_and_duration(self):
        """
        Try passing a list of durations, and make sure the encoded
        timestamps and durations are correct.
        """

        durations = [0, 10, 20, 30, 40]
        temp_file = self.tempfile("temp.webp")
        frame1 = Image.open('Tests/images/anim_frame1.webp')
        frame2 = Image.open('Tests/images/anim_frame2.webp')
        frame1.save(temp_file, save_all=True,
                    append_images=[frame2, frame1, frame2, frame1],
                    duration=durations)

        im = Image.open(temp_file)
        self.assertEqual(im.n_frames, 5)
        self.assertTrue(im.is_animated)

        # Double-check that timestamps and durations match original values specified
        ts = 0
        for frame in range(im.n_frames):
            im.seek(frame)
            im.load()
            self.assertEqual(im.info["duration"], durations[frame])
            self.assertEqual(im.info["timestamp"], ts)
            ts += durations[frame]

    def test_seeking(self):
        """
        Create an animated webp file, and then try seeking through
        frames in reverse-order, verifying the timestamps and durations
        are correct.
        """

        dur = 33
        temp_file = self.tempfile("temp.webp")
        frame1 = Image.open('Tests/images/anim_frame1.webp')
        frame2 = Image.open('Tests/images/anim_frame2.webp')
        frame1.save(temp_file, save_all=True,
                    append_images=[frame2, frame1, frame2, frame1],
                    duration=dur)

        im = Image.open(temp_file)
        self.assertEqual(im.n_frames, 5)
        self.assertTrue(im.is_animated)

        # Traverse frames in reverse order, double-check timestamps and duration
        ts = dur * (im.n_frames-1)
        for frame in reversed(range(im.n_frames)):
            im.seek(frame)
            im.load()
            self.assertEqual(im.info["duration"], dur)
            self.assertEqual(im.info["timestamp"], ts)
            ts -= dur


if __name__ == '__main__':
    unittest.main()
