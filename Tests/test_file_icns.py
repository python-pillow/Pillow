from helper import unittest, PillowTestCase, hopper

import io
from PIL import Image

# sample icon file
file = "Tests/images/pillow.icns"
data = open(file, "rb").read()

enable_jpeg2k = hasattr(Image.core, 'jp2klib_version')


class TestFileIcns(PillowTestCase):

    def test_sanity(self):
        # Loading this icon by default should result in the largest size
        # (512x512@2x) being loaded
        im = Image.open(file)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (1024, 1024))
        self.assertEqual(im.format, "ICNS")

    def test_sizes(self):
        # Check that we can load all of the sizes, and that the final pixel
        # dimensions are as expected
        im = Image.open(file)
        for w, h, r in im.info['sizes']:
            wr = w * r
            hr = h * r
            im2 = Image.open(file)
            im2.size = (w, h, r)
            im2.load()
            self.assertEqual(im2.mode, 'RGBA')
            self.assertEqual(im2.size, (wr, hr))

    def test_older_icon(self):
        # This icon was made with Icon Composer rather than iconutil; it still
        # uses PNG rather than JP2, however (since it was made on 10.9).
        im = Image.open('Tests/images/pillow2.icns')
        for w, h, r in im.info['sizes']:
            wr = w * r
            hr = h * r
            im2 = Image.open('Tests/images/pillow2.icns')
            im2.size = (w, h, r)
            im2.load()
            self.assertEqual(im2.mode, 'RGBA')
            self.assertEqual(im2.size, (wr, hr))

    def test_jp2_icon(self):
        # This icon was made by using Uli Kusterer's oldiconutil to replace
        # the PNG images with JPEG 2000 ones.  The advantage of doing this is
        # that OS X 10.5 supports JPEG 2000 but not PNG; some commercial
        # software therefore does just this.

        # (oldiconutil is here: https://github.com/uliwitness/oldiconutil)

        if not enable_jpeg2k:
            return

        im = Image.open('Tests/images/pillow3.icns')
        for w, h, r in im.info['sizes']:
            wr = w * r
            hr = h * r
            im2 = Image.open('Tests/images/pillow3.icns')
            im2.size = (w, h, r)
            im2.load()
            self.assertEqual(im2.mode, 'RGBA')
            self.assertEqual(im2.size, (wr, hr))

    def test_save_to_bytes(self):
        output = io.BytesIO()
        im = hopper()
        sizes = [(16, 16, 1), (16, 16, 2),
                 (32, 32, 1), (32, 32, 2),
                 (128, 128, 1)]
        im.save(output, "icns", sizes=sizes)
        output.seek(0)
        reloaded = Image.open(output)
        self.assertEqual(reloaded.mode, "RGBA")
        self.assertEqual(reloaded.format, "ICNS")
        self.assertEqual(set(reloaded.info['sizes']), set(sizes))
        for w, h, r in reloaded.info['sizes']:
            wr = w * r
            hr = h * r
            im2 = Image.open(file)
            im2.size = (w, h, r)
            im2.load()
            self.assertEqual(im2.mode, 'RGBA')
            self.assertEqual(im2.size, (wr, hr))


if __name__ == '__main__':
    unittest.main()

# End of file
