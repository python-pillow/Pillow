from helper import unittest, PillowTestCase, hopper

from PIL import Image
import os
import sys


class TestImage(PillowTestCase):

    def test_image_modes_success(self):
        for mode in [
            '1', 'P', 'PA',
            'L', 'LA', 'La',
            'F', 'I', 'I;16', 'I;16L', 'I;16B', 'I;16N',
            'RGB', 'RGBX', 'RGBA', 'RGBa',
            'CMYK', 'YCbCr', 'LAB', 'HSV',
        ]:
            Image.new(mode, (1, 1))

    def test_image_modes_fail(self):
        for mode in [
            '', 'bad', 'very very long',
            'BGR;15', 'BGR;16', 'BGR;24', 'BGR;32'
        ]:
            with self.assertRaises(ValueError) as e:
                Image.new(mode, (1, 1));
            self.assertEqual(str(e.exception), 'unrecognized image mode')

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
        self.assertRaises(ValueError, lambda: Image.new("", (100, 100)))
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
        with tempfile.TemporaryFile() as fp:
            im.save(fp, 'JPEG')
            fp.seek(0)
            reloaded = Image.open(fp)
            self.assert_image_similar(im, reloaded, 20)

    def test_unknown_extension(self):
        im = hopper()
        temp_file = self.tempfile("temp.unknown")
        self.assertRaises(ValueError, lambda: im.save(temp_file))

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
        # Assert
        self.assertEqual(hopper('RGB').getbands(), ('R', 'G', 'B'))
        self.assertEqual(hopper('YCbCr').getbands(), ('Y', 'Cb', 'Cr'))

    def test_getchannel_wrong_params(self):
        im = hopper()

        self.assertRaises(ValueError, im.getchannel, -1)
        self.assertRaises(ValueError, im.getchannel, 3)
        self.assertRaises(ValueError, im.getchannel, 'Z')
        self.assertRaises(ValueError, im.getchannel, '1')

    def test_getchannel(self):
        im = hopper('YCbCr')
        Y, Cb, Cr = im.split()

        self.assert_image_equal(Y, im.getchannel(0))
        self.assert_image_equal(Y, im.getchannel('Y'))
        self.assert_image_equal(Cb, im.getchannel(1))
        self.assert_image_equal(Cb, im.getchannel('Cb'))
        self.assert_image_equal(Cr, im.getchannel(2))
        self.assert_image_equal(Cr, im.getchannel('Cr'))

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
        self.assertNotEqual(im1, im2)

    def test_alpha_composite(self):
        # https://stackoverflow.com/questions/3374878
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

    def test_alpha_inplace(self):
        src = Image.new('RGBA', (128,128), 'blue')

        over = Image.new('RGBA', (128,128), 'red')
        mask = hopper('L')
        over.putalpha(mask)

        target = Image.alpha_composite(src, over)

        # basic
        full = src.copy()
        full.alpha_composite(over)
        self.assert_image_equal(full, target)

        # with offset down to right
        offset = src.copy()
        offset.alpha_composite(over, (64, 64))
        self.assert_image_equal(offset.crop((64, 64, 127, 127)),
                                target.crop((0, 0, 63, 63)))
        self.assertEqual(offset.size, (128, 128))

        # offset and crop
        box = src.copy()
        box.alpha_composite(over, (64, 64), (0, 0, 32, 32))
        self.assert_image_equal(box.crop((64, 64, 96, 96)),
                                target.crop((0, 0, 32, 32)))
        self.assert_image_equal(box.crop((96, 96, 128, 128)),
                                src.crop((0, 0, 32, 32)))
        self.assertEqual(box.size, (128, 128))

        # source point
        source = src.copy()
        source.alpha_composite(over, (32, 32), (32, 32, 96, 96))

        self.assert_image_equal(source.crop((32, 32, 96, 96)),
                                target.crop((32, 32, 96, 96)))
        self.assertEqual(source.size, (128, 128))

    def test_registered_extensions_uninitialized(self):
        # Arrange
        Image._initialized = 0
        extension = Image.EXTENSION
        Image.EXTENSION = {}

        # Act
        Image.registered_extensions()

        # Assert
        self.assertEqual(Image._initialized, 2)

        # Restore the original state and assert
        Image.EXTENSION = extension
        self.assertTrue(Image.EXTENSION)

    def test_registered_extensions(self):
        # Arrange
        # Open an image to trigger plugin registration
        Image.open('Tests/images/rgb.jpg')

        # Act
        extensions = Image.registered_extensions()

        # Assert
        self.assertTrue(bool(extensions))
        for ext in ['.cur', '.icns', '.tif', '.tiff']:
            self.assertIn(ext, extensions)

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
        # Checking that the _check_size function throws value errors
        # when we want it to.
        with self.assertRaises(ValueError):
            Image.new('RGB', 0)  # not a tuple
        with self.assertRaises(ValueError):
            Image.new('RGB', (0,))  # Tuple too short
        with self.assertRaises(ValueError):
            Image.new('RGB', (-1, -1))  # w,h < 0

        # this should pass with 0 sized images, #2259
        im = Image.new('L', (0, 0))
        self.assertEqual(im.size, (0, 0))

        self.assertTrue(Image.new('RGB', (1, 1)))
        # Should pass lists too
        i = Image.new('RGB', [1, 1])
        self.assertIsInstance(i.size, tuple)

    def test_storage_neg(self):
        # Storage.c accepted negative values for xsize, ysize.  Was
        # test_neg_ppm, but the core function for that has been
        # removed Calling directly into core to test the error in
        # Storage.c, rather than the size check above

        with self.assertRaises(ValueError):
            Image.core.fill('RGB', (2, -2), (0, 0, 0))

    def test_offset_not_implemented(self):
        # Arrange
        im = hopper()

        # Act / Assert
        self.assertRaises(NotImplementedError, lambda: im.offset(None))

    def test_fromstring(self):
        self.assertRaises(NotImplementedError, Image.fromstring)

    def test_linear_gradient_wrong_mode(self):
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        self.assertRaises(ValueError,
                          lambda: Image.linear_gradient(wrong_mode))
        return

    def test_linear_gradient(self):

        # Arrange
        target_file = "Tests/images/linear_gradient.png"
        for mode in ["L", "P"]:

            # Act
            im = Image.linear_gradient(mode)

            # Assert
            self.assertEqual(im.size, (256, 256))
            self.assertEqual(im.mode, mode)
            self.assertEqual(im.getpixel((0, 0)), 0)
            self.assertEqual(im.getpixel((255, 255)), 255)
            target = Image.open(target_file).convert(mode)
            self.assert_image_equal(im, target)

    def test_radial_gradient_wrong_mode(self):
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        self.assertRaises(ValueError,
                          lambda: Image.radial_gradient(wrong_mode))
        return

    def test_radial_gradient(self):

        # Arrange
        target_file = "Tests/images/radial_gradient.png"
        for mode in ["L", "P"]:

            # Act
            im = Image.radial_gradient(mode)

            # Assert
            self.assertEqual(im.size, (256, 256))
            self.assertEqual(im.mode, mode)
            self.assertEqual(im.getpixel((0, 0)), 255)
            self.assertEqual(im.getpixel((128, 128)), 0)
            target = Image.open(target_file).convert(mode)
            self.assert_image_equal(im, target)


class MockEncoder(object):
    pass


def mock_encode(*args):
    encoder = MockEncoder()
    encoder.args = args
    return encoder


class TestRegistry(PillowTestCase):

    def test_encode_registry(self):

        Image.register_encoder('MOCK', mock_encode)
        self.assertIn('MOCK', Image.ENCODERS)

        enc = Image._getencoder('RGB', 'MOCK', ('args',), extra=('extra',))

        self.assertIsInstance(enc, MockEncoder)
        self.assertEqual(enc.args, ('RGB', 'args', 'extra'))

    def test_encode_registry_fail(self):
        self.assertRaises(IOError, lambda: Image._getencoder('RGB',
                                                             'DoesNotExist',
                                                             ('args',),
                                                             extra=('extra',)))

if __name__ == '__main__':
    unittest.main()
