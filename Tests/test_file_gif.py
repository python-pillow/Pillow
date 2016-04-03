from helper import unittest, PillowTestCase, hopper, netpbm_available

from PIL import Image
from PIL import GifImagePlugin

codecs = dir(Image.core)

# sample gif stream
TEST_GIF = "Tests/images/hopper.gif"

with open(TEST_GIF, "rb") as f:
    data = f.read()


class TestFileGif(PillowTestCase):

    def setUp(self):
        if "gif_encoder" not in codecs or "gif_decoder" not in codecs:
            self.skipTest("gif support not available")  # can this happen?

    def test_sanity(self):
        im = Image.open(TEST_GIF)
        im.load()
        self.assertEqual(im.mode, "P")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "GIF")
        self.assertEqual(im.info["version"], b"GIF89a")

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: GifImagePlugin.GifImageFile(invalid_file))

    def test_optimize(self):
        from io import BytesIO

        def test_grayscale(optimize):
            im = Image.new("L", (1, 1), 0)
            filename = BytesIO()
            im.save(filename, "GIF", optimize=optimize)
            return len(filename.getvalue())

        def test_bilevel(optimize):
            im = Image.new("1", (1, 1), 0)
            test_file = BytesIO()
            im.save(test_file, "GIF", optimize=optimize)
            return len(test_file.getvalue())

        self.assertEqual(test_grayscale(0), 800)
        self.assertEqual(test_grayscale(1), 38)
        self.assertEqual(test_bilevel(0), 800)
        self.assertEqual(test_bilevel(1), 800)

    def test_optimize_full_l(self):
        from io import BytesIO

        im = Image.frombytes("L", (16, 16), bytes(bytearray(range(256))))
        test_file = BytesIO()
        im.save(test_file, "GIF", optimize=True)
        self.assertEqual(im.mode, "L")

    def test_roundtrip(self):
        out = self.tempfile('temp.gif')
        im = hopper()
        im.save(out)
        reread = Image.open(out)

        self.assert_image_similar(reread.convert('RGB'), im, 50)

    def test_roundtrip2(self):
        # see https://github.com/python-pillow/Pillow/issues/403
        out = self.tempfile('temp.gif')
        im = Image.open(TEST_GIF)
        im2 = im.copy()
        im2.save(out)
        reread = Image.open(out)

        self.assert_image_similar(reread.convert('RGB'), hopper(), 50)

    def test_roundtrip_save_all(self):
        # Single frame image
        out = self.tempfile('temp.gif')
        im = hopper()
        im.save(out, save_all=True)
        reread = Image.open(out)

        self.assert_image_similar(reread.convert('RGB'), im, 50)

        # Multiframe image
        im = Image.open("Tests/images/dispose_bgnd.gif")

        out = self.tempfile('temp.gif')
        im.save(out, save_all=True)
        reread = Image.open(out)

        self.assertEqual(reread.n_frames, 5)

    def test_headers_saving_for_animated_gifs(self):
        important_headers = ['background', 'version', 'duration', 'loop']
        # Multiframe image
        im = Image.open("Tests/images/dispose_bgnd.gif")

        out = self.tempfile('temp.gif')
        im.save(out, save_all=True)
        reread = Image.open(out)

        for header in important_headers:
            self.assertEqual(
                im.info[header],
                reread.info[header]
            )

    def test_palette_handling(self):
        # see https://github.com/python-pillow/Pillow/issues/513

        im = Image.open(TEST_GIF)
        im = im.convert('RGB')

        im = im.resize((100, 100), Image.LANCZOS)
        im2 = im.convert('P', palette=Image.ADAPTIVE, colors=256)

        f = self.tempfile('temp.gif')
        im2.save(f, optimize=True)

        reloaded = Image.open(f)

        self.assert_image_similar(im, reloaded.convert('RGB'), 10)

    def test_palette_434(self):
        # see https://github.com/python-pillow/Pillow/issues/434

        def roundtrip(im, *args, **kwargs):
            out = self.tempfile('temp.gif')
            im.copy().save(out, *args, **kwargs)
            reloaded = Image.open(out)

            return reloaded

        orig = "Tests/images/test.colors.gif"
        im = Image.open(orig)

        self.assert_image_similar(im, roundtrip(im), 1)
        self.assert_image_similar(im, roundtrip(im, optimize=True), 1)

        im = im.convert("RGB")
        # check automatic P conversion
        reloaded = roundtrip(im).convert('RGB')
        self.assert_image_equal(im, reloaded)

    @unittest.skipUnless(netpbm_available(), "netpbm not available")
    def test_save_netpbm_bmp_mode(self):
        img = Image.open(TEST_GIF).convert("RGB")

        tempfile = self.tempfile("temp.gif")
        GifImagePlugin._save_netpbm(img, 0, tempfile)
        self.assert_image_similar(img, Image.open(tempfile).convert("RGB"), 0)

    @unittest.skipUnless(netpbm_available(), "netpbm not available")
    def test_save_netpbm_l_mode(self):
        img = Image.open(TEST_GIF).convert("L")

        tempfile = self.tempfile("temp.gif")
        GifImagePlugin._save_netpbm(img, 0, tempfile)
        self.assert_image_similar(img, Image.open(tempfile).convert("L"), 0)

    def test_seek(self):
        img = Image.open("Tests/images/dispose_none.gif")
        framecount = 0
        try:
            while True:
                framecount += 1
                img.seek(img.tell() + 1)
        except EOFError:
            self.assertEqual(framecount, 5)

    def test_n_frames(self):
        im = Image.open(TEST_GIF)
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

        im = Image.open("Tests/images/iss634.gif")
        self.assertEqual(im.n_frames, 42)
        self.assertTrue(im.is_animated)

    def test_eoferror(self):
        im = Image.open(TEST_GIF)

        n_frames = im.n_frames
        while True:
            n_frames -= 1
            try:
                im.seek(n_frames)
                break
            except EOFError:
                self.assertTrue(im.tell() < n_frames)

    def test_dispose_none(self):
        img = Image.open("Tests/images/dispose_none.gif")
        try:
            while True:
                img.seek(img.tell() + 1)
                self.assertEqual(img.disposal_method, 1)
        except EOFError:
            pass

    def test_dispose_background(self):
        img = Image.open("Tests/images/dispose_bgnd.gif")
        try:
            while True:
                img.seek(img.tell() + 1)
                self.assertEqual(img.disposal_method, 2)
        except EOFError:
            pass

    def test_dispose_previous(self):
        img = Image.open("Tests/images/dispose_prev.gif")
        try:
            while True:
                img.seek(img.tell() + 1)
                self.assertEqual(img.disposal_method, 3)
        except EOFError:
            pass

    def test_iss634(self):
        img = Image.open("Tests/images/iss634.gif")
        # seek to the second frame
        img.seek(img.tell() + 1)
        # all transparent pixels should be replaced with the color from the
        # first frame
        self.assertEqual(img.histogram()[img.info['transparency']], 0)

    def test_duration(self):
        duration = 1000

        out = self.tempfile('temp.gif')
        fp = open(out, "wb")
        im = Image.new('L', (100, 100), '#000')
        for s in GifImagePlugin.getheader(im)[0] + GifImagePlugin.getdata(im, duration=duration):
            fp.write(s)
        fp.write(b";")
        fp.close()
        reread = Image.open(out)

        self.assertEqual(reread.info['duration'], duration)

    def test_number_of_loops(self):
        number_of_loops = 2

        out = self.tempfile('temp.gif')
        fp = open(out, "wb")
        im = Image.new('L', (100, 100), '#000')
        for s in GifImagePlugin.getheader(im)[0] + GifImagePlugin.getdata(im, loop=number_of_loops):
            fp.write(s)
        fp.write(b";")
        fp.close()
        reread = Image.open(out)

        self.assertEqual(reread.info['loop'], number_of_loops)

    def test_background(self):
        out = self.tempfile('temp.gif')
        im = Image.new('L', (100, 100), '#000')
        im.info['background'] = 1
        im.save(out)
        reread = Image.open(out)

        self.assertEqual(reread.info['background'], im.info['background'])

    def test_version(self):
        out = self.tempfile('temp.gif')

        # Test that GIF87a is used by default
        im = Image.new('L', (100, 100), '#000')
        im.save(out)
        reread = Image.open(out)
        self.assertEqual(reread.info["version"], b"GIF87a")

        # Test that adding a GIF89a feature changes the version
        im.info["transparency"] = 1
        im.save(out)
        reread = Image.open(out)
        self.assertEqual(reread.info["version"], b"GIF89a")

        # Test that a GIF87a image is also saved in that format
        im = Image.open(TEST_GIF)
        im.save(out)
        reread = Image.open(out)
        self.assertEqual(reread.info["version"], b"GIF87a")

        # Test that a GIF89a image is also saved in that format
        im.info["version"] = "GIF89a"
        im.save(out)
        reread = Image.open(out)
        self.assertEqual(reread.info["version"], b"GIF87a")


if __name__ == '__main__':
    unittest.main()

# End of file
