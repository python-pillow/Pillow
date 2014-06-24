from helper import unittest, PillowTestCase, tearDownModule

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

if __name__ == '__main__':
    unittest.main()

# End of file
