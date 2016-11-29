from helper import unittest, PillowTestCase, hopper

from PIL import Image
import os
import sys


class TestImage(PillowTestCase):

    def test_sanity(self):

        im = Image.new("L", (100, 100))
        self.assertEqual(
            repr(im)[:45], "<PIL.Image.Image image mode=L size=100x100 at")
        self.assertEqual(im.mode, "L")
        self.assertEqual(im.size, (100, 100))

        im = Image.new("RGB", (100, 100))
        self.assertEqual(
            repr(im)[:45], "<PIL.Image.Image image mode=RGB size=100x100 ")
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (100, 100))

        Image.new("L", (100, 100), None)
        im2 = Image.new("L", (100, 100), 0)
        im3 = Image.new("L", (100, 100), "black")

        self.assertEqual(im2.getcolors(), [(10000, 0)])
        self.assertEqual(im3.getcolors(), [(10000, 0)])

        self.assertRaises(ValueError, lambda: Image.new("X", (100, 100)))
        # self.assertRaises(
        #     MemoryError, lambda: Image.new("L", (1000000, 1000000)))

    def test_width_height(self):
        im = Image.new("RGB", (1, 2))
        self.assertEqual(im.width, 1)
        self.assertEqual(im.height, 2)

        im.size = (3, 4)
        self.assertEqual(im.width, 3)
        self.assertEqual(im.height, 4)

    def test_invalid_image(self):
        if str is bytes:
            import StringIO
            im = StringIO.StringIO('')
        else:
            import io
            im = io.BytesIO(b'')
        self.assertRaises(IOError, lambda: Image.open(im))

    @unittest.skipIf(sys.version_info < (3, 4),
                     "pathlib only available in Python 3.4 or later")
    def test_pathlib(self):
        from pathlib import Path
        im = Image.open(Path("Tests/images/hopper.jpg"))
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))

        temp_file = self.tempfile("temp.jpg")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        im.save(Path(temp_file))

    def test_fp_name(self):
        temp_file = self.tempfile("temp.jpg")

        class FP(object):
            def write(a, b):
                pass
        fp = FP()
        fp.name = temp_file

        im = hopper()
        im.save(fp)

    def test_tempfile(self):
        # see #1460, pathlib support breaks tempfile.TemporaryFile on py27
        # Will error out on save on 3.0.0
        import tempfile
        im = hopper()
        fp = tempfile.TemporaryFile()
        im.save(fp, 'JPEG')
        fp.seek(0)
        reloaded = Image.open(fp)
        self.assert_image_similar(im, reloaded, 20)

    def test_internals(self):

        im = Image.new("L", (100, 100))
        im.readonly = 1
        im._copy()
        self.assertFalse(im.readonly)

        im.readonly = 1
        im.paste(0, (0, 0, 100, 100))
        self.assertFalse(im.readonly)

        test_file = self.tempfile("temp.ppm")
        im._dump(test_file)

    def test_comparison_with_other_type(self):
        # Arrange
        item = Image.new('RGB', (25, 25), '#000')
        num = 12

        # Act/Assert
        # Shouldn't cause AttributeError (#774)
        self.assertFalse(item is None)
        self.assertFalse(item == None)
        self.assertFalse(item == num)

    def test_expand_x(self):
        # Arrange
        im = hopper()
        orig_size = im.size
        xmargin = 5

        # Act
        im = im._expand(xmargin)

        # Assert
        self.assertEqual(im.size[0], orig_size[0] + 2*xmargin)
        self.assertEqual(im.size[1], orig_size[1] + 2*xmargin)

    def test_expand_xy(self):
        # Arrange
        im = hopper()
        orig_size = im.size
        xmargin = 5
        ymargin = 3

        # Act
        im = im._expand(xmargin, ymargin)

        # Assert
        self.assertEqual(im.size[0], orig_size[0] + 2*xmargin)
        self.assertEqual(im.size[1], orig_size[1] + 2*ymargin)

    def test_getbands(self):
        # Arrange
        im = hopper()

        # Act
        bands = im.getbands()

        # Assert
        self.assertEqual(bands, ('R', 'G', 'B'))

    def test_getbbox(self):
        # Arrange
        im = hopper()

        # Act
        bbox = im.getbbox()

        # Assert
        self.assertEqual(bbox, (0, 0, 128, 128))

    def test_ne(self):
        # Arrange
        im1 = Image.new('RGB', (25, 25), 'black')
        im2 = Image.new('RGB', (25, 25), 'white')

        # Act / Assert
        self.assertTrue(im1 != im2)

    def test_alpha_composite(self):
        # http://stackoverflow.com/questions/3374878
        # Arrange
        from PIL import ImageDraw

        expected_colors = sorted([
            (1122, (128, 127, 0, 255)),
            (1089, (0, 255, 0, 255)),
            (3300, (255, 0, 0, 255)),
            (1156, (170, 85, 0, 192)),
            (1122, (0, 255, 0, 128)),
            (1122, (255, 0, 0, 128)),
            (1089, (0, 255, 0, 0))])

        dst = Image.new('RGBA', size=(100, 100), color=(0, 255, 0, 255))
        draw = ImageDraw.Draw(dst)
        draw.rectangle((0, 33, 100, 66), fill=(0, 255, 0, 128))
        draw.rectangle((0, 67, 100, 100), fill=(0, 255, 0, 0))
        src = Image.new('RGBA', size=(100, 100), color=(255, 0, 0, 255))
        draw = ImageDraw.Draw(src)
        draw.rectangle((33, 0, 66, 100), fill=(255, 0, 0, 128))
        draw.rectangle((67, 0, 100, 100), fill=(255, 0, 0, 0))

        # Act
        img = Image.alpha_composite(dst, src)

        # Assert
        img_colors = sorted(img.getcolors())
        self.assertEqual(img_colors, expected_colors)

    def test_effect_mandelbrot(self):
        # Arrange
        size = (512, 512)
        extent = (-3, -2.5, 2, 2.5)
        quality = 100

        # Act
        im = Image.effect_mandelbrot(size, extent, quality)

        # Assert
        self.assertEqual(im.size, (512, 512))
        im2 = Image.open('Tests/images/effect_mandelbrot.png')
        self.assert_image_equal(im, im2)

    def test_effect_mandelbrot_bad_arguments(self):
        # Arrange
        size = (512, 512)
        # Get coordinates the wrong way round:
        extent = (+3, +2.5, -2, -2.5)
        # Quality < 2:
        quality = 1

        # Act/Assert
        self.assertRaises(
            ValueError,
            lambda: Image.effect_mandelbrot(size, extent, quality))

    def test_effect_noise(self):
        # Arrange
        size = (100, 100)
        sigma = 128

        # Act
        im = Image.effect_noise(size, sigma)

        # Assert
        self.assertEqual(im.size, (100, 100))
        self.assertEqual(im.mode, "L")
        self.assertNotEqual(im.getpixel((0, 0)), im.getpixel((0, 1)))

    def test_effect_spread(self):
        # Arrange
        im = hopper()
        distance = 10

        # Act
        im2 = im.effect_spread(distance)

        # Assert
        self.assertEqual(im.size, (128, 128))
        im3 = Image.open('Tests/images/effect_spread.png')
        self.assert_image_similar(im2, im3, 110)

    def test_check_size(self):
        # Checking that the _check_size function throws value errors when we want it to.
        with self.assertRaises(ValueError):
            Image.new('RGB', 0)  # not a tuple
        with self.assertRaises(ValueError):
            Image.new('RGB', (0,))  # Tuple too short
        with self.assertRaises(ValueError):
            Image.new('RGB', (-1,-1))  # w,h < 0

        # this should pass with 0 sized images, #2259
        im = Image.new('L', (0, 0))
        self.assertEqual(im.size, (0, 0))

        self.assertTrue(Image.new('RGB', (1,1)))
        # Should pass lists too
        i = Image.new('RGB', [1,1])
        self.assertIsInstance(i.size, tuple)

    def test_storage_neg(self):
        # Storage.c accepted negative values for xsize, ysize.  Was
        # test_neg_ppm, but the core function for that has been
        # removed Calling directly into core to test the error in
        # Storage.c, rather than the size check above

        with self.assertRaises(ValueError):
            Image.core.fill('RGB', (2,-2), (0,0,0))


if __name__ == '__main__':
    unittest.main()
