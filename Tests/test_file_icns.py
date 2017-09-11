from helper import unittest, PillowTestCase

from PIL import Image, IcnsImagePlugin

import io
import sys

# sample icon file
TEST_FILE = "Tests/images/pillow.icns"

enable_jpeg2k = hasattr(Image.core, 'jp2klib_version')


class TestFileIcns(PillowTestCase):

    def test_sanity(self):
        # Loading this icon by default should result in the largest size
        # (512x512@2x) being loaded
        im = Image.open(TEST_FILE)
        im.load()
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (1024, 1024))
        self.assertEqual(im.format, "ICNS")

    @unittest.skipIf(sys.platform != 'darwin',
                     "requires MacOS")
    def test_save(self):
        im = Image.open(TEST_FILE)

        temp_file = self.tempfile("temp.icns")
        im.save(temp_file)

        reread = Image.open(temp_file)

        self.assertEqual(reread.mode, "RGBA")
        self.assertEqual(reread.size, (1024, 1024))
        self.assertEqual(reread.format, "ICNS")

    def test_sizes(self):
        # Check that we can load all of the sizes, and that the final pixel
        # dimensions are as expected
        im = Image.open(TEST_FILE)
        for w, h, r in im.info['sizes']:
            wr = w * r
            hr = h * r
            im2 = Image.open(TEST_FILE)
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

    def test_getimage(self):
        with open(TEST_FILE, 'rb') as fp:
            icns_file = IcnsImagePlugin.IcnsFile(fp)

            im = icns_file.getimage()
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (1024, 1024))

            im = icns_file.getimage((512, 512))
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (512, 512))

    def test_not_an_icns_file(self):
        with io.BytesIO(b'invalid\n') as fp:
            self.assertRaises(SyntaxError,
                              IcnsImagePlugin.IcnsFile, fp)


if __name__ == '__main__':
    unittest.main()
