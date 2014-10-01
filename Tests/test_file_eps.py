from helper import unittest, PillowTestCase

from PIL import Image, EpsImagePlugin
import io

# Our two EPS test files (they are identical except for their bounding boxes)
file1 = "Tests/images/zero_bb.eps"
file2 = "Tests/images/non_zero_bb.eps"

# Due to palletization, we'll need to convert these to RGB after load
file1_compare = "Tests/images/zero_bb.png"
file1_compare_scale2 = "Tests/images/zero_bb_scale2.png"

file2_compare = "Tests/images/non_zero_bb.png"
file2_compare_scale2 = "Tests/images/non_zero_bb_scale2.png"

# EPS test files with binary preview
file3 = "Tests/images/binary_preview_map.eps"


class TestFileEps(PillowTestCase):

    def setUp(self):
        if not EpsImagePlugin.has_ghostscript():
            self.skipTest("Ghostscript not available")

    def test_sanity(self):
        # Regular scale
        image1 = Image.open(file1)
        image1.load()
        self.assertEqual(image1.mode, "RGB")
        self.assertEqual(image1.size, (460, 352))
        self.assertEqual(image1.format, "EPS")

        image2 = Image.open(file2)
        image2.load()
        self.assertEqual(image2.mode, "RGB")
        self.assertEqual(image2.size, (360, 252))
        self.assertEqual(image2.format, "EPS")

        # Double scale
        image1_scale2 = Image.open(file1)
        image1_scale2.load(scale=2)
        self.assertEqual(image1_scale2.mode, "RGB")
        self.assertEqual(image1_scale2.size, (920, 704))
        self.assertEqual(image1_scale2.format, "EPS")

        image2_scale2 = Image.open(file2)
        image2_scale2.load(scale=2)
        self.assertEqual(image2_scale2.mode, "RGB")
        self.assertEqual(image2_scale2.size, (720, 504))
        self.assertEqual(image2_scale2.format, "EPS")

    def test_file_object(self):
        # issue 479
        image1 = Image.open(file1)
        with open(self.tempfile('temp_file.eps'), 'wb') as fh:
            image1.save(fh, 'EPS')

    def test_iobase_object(self):
        # issue 479
        image1 = Image.open(file1)
        with io.open(self.tempfile('temp_iobase.eps'), 'wb') as fh:
            image1.save(fh, 'EPS')

    def test_bytesio_object(self):
        with open(file1, 'rb') as f:
            img_bytes = io.BytesIO(f.read())

        img = Image.open(img_bytes)
        img.load()

        image1_scale1_compare = Image.open(file1_compare).convert("RGB")
        image1_scale1_compare.load()
        self.assert_image_similar(img, image1_scale1_compare, 5)

    def test_render_scale1(self):
        # We need png support for these render test
        codecs = dir(Image.core)
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zip/deflate support not available")

        # Zero bounding box
        image1_scale1 = Image.open(file1)
        image1_scale1.load()
        image1_scale1_compare = Image.open(file1_compare).convert("RGB")
        image1_scale1_compare.load()
        self.assert_image_similar(image1_scale1, image1_scale1_compare, 5)

        # Non-Zero bounding box
        image2_scale1 = Image.open(file2)
        image2_scale1.load()
        image2_scale1_compare = Image.open(file2_compare).convert("RGB")
        image2_scale1_compare.load()
        self.assert_image_similar(image2_scale1, image2_scale1_compare, 10)

    def test_render_scale2(self):
        # We need png support for these render test
        codecs = dir(Image.core)
        if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
            self.skipTest("zip/deflate support not available")

        # Zero bounding box
        image1_scale2 = Image.open(file1)
        image1_scale2.load(scale=2)
        image1_scale2_compare = Image.open(file1_compare_scale2).convert("RGB")
        image1_scale2_compare.load()
        self.assert_image_similar(image1_scale2, image1_scale2_compare, 5)

        # Non-Zero bounding box
        image2_scale2 = Image.open(file2)
        image2_scale2.load(scale=2)
        image2_scale2_compare = Image.open(file2_compare_scale2).convert("RGB")
        image2_scale2_compare.load()
        self.assert_image_similar(image2_scale2, image2_scale2_compare, 10)

    def test_resize(self):
        # Arrange
        image1 = Image.open(file1)
        image2 = Image.open(file2)
        new_size = (100, 100)

        # Act
        image1 = image1.resize(new_size)
        image2 = image2.resize(new_size)

        # Assert
        self.assertEqual(image1.size, new_size)
        self.assertEqual(image2.size, new_size)

    def test_thumbnail(self):
        # Issue #619
        # Arrange
        image1 = Image.open(file1)
        image2 = Image.open(file2)
        new_size = (100, 100)

        # Act
        image1.thumbnail(new_size)
        image2.thumbnail(new_size)

        # Assert
        self.assertEqual(max(image1.size), max(new_size))
        self.assertEqual(max(image2.size), max(new_size))

    def test_read_binary_preview(self):
        # Issue 302
        # open image with binary preview
        Image.open(file3)

    def _test_readline(self,t, ending):
        ending = "Failure with line ending: %s" %("".join("%s" %ord(s) for s in ending))
        self.assertEqual(t.readline().strip('\r\n'), 'something', ending)
        self.assertEqual(t.readline().strip('\r\n'), 'else', ending)
        self.assertEqual(t.readline().strip('\r\n'), 'baz', ending)
        self.assertEqual(t.readline().strip('\r\n'), 'bif', ending)

    def _test_readline_stringio(self, test_string, ending):
        # check all the freaking line endings possible
        try:
            import StringIO
        except:
            # don't skip, it skips everything in the parent test
            return
        t = StringIO.StringIO(test_string)
        self._test_readline(t, ending)

    def _test_readline_io(self, test_string, ending):
        if str is bytes:
            t = io.StringIO(unicode(test_string))
        else:
            t = io.StringIO(test_string)
        self._test_readline(t, ending)

    def _test_readline_file_universal(self, test_string, ending):
        f = self.tempfile('temp.txt')
        with open(f,'wb') as w:
            if str is bytes:
                w.write(test_string)
            else:
                w.write(test_string.encode('UTF-8'))

        with open(f,'rU') as t:
            self._test_readline(t, ending)

    def _test_readline_file_psfile(self, test_string, ending):
        f = self.tempfile('temp.txt')
        with open(f,'wb') as w:
            if str is bytes:
                w.write(test_string)
            else:
                w.write(test_string.encode('UTF-8'))

        with open(f,'rb') as r:
            t = EpsImagePlugin.PSFile(r)
            self._test_readline(t, ending)

    def test_readline(self):
        # check all the freaking line endings possible from the spec
        #test_string = u'something\r\nelse\n\rbaz\rbif\n'
        line_endings = ['\r\n', '\n']
        not_working_endings = ['\n\r', '\r']
        strings = ['something', 'else', 'baz', 'bif']

        for ending in line_endings:
            s = ending.join(strings)
            # Native Python versions will pass these endings.
            #self._test_readline_stringio(s, ending)
            #self._test_readline_io(s, ending)
            #self._test_readline_file_universal(s, ending)

            self._test_readline_file_psfile(s, ending)

        for ending in not_working_endings:
            # these only work with the PSFile, while they're in spec,
            # they're not likely to be used
            s = ending.join(strings)

            # Native Python versions may fail on these endings.
            #self._test_readline_stringio(s, ending)
            #self._test_readline_io(s, ending)
            #self._test_readline_file_universal(s, ending)

            self._test_readline_file_psfile(s, ending)


if __name__ == '__main__':
    unittest.main()

# End of file
