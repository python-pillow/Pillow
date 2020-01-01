import io
import os
import shutil
import tempfile
import unittest

from PIL import Image, UnidentifiedImageError

from .helper import PillowTestCase, hopper, is_win32


class TestImage(PillowTestCase):
    def test_image_modes_success(self):
        for mode in [
            "1",
            "P",
            "PA",
            "L",
            "LA",
            "La",
            "F",
            "I",
            "I;16",
            "I;16L",
            "I;16B",
            "I;16N",
            "RGB",
            "RGBX",
            "RGBA",
            "RGBa",
            "CMYK",
            "YCbCr",
            "LAB",
            "HSV",
        ]:
            Image.new(mode, (1, 1))

    def test_image_modes_fail(self):
        for mode in [
            "",
            "bad",
            "very very long",
            "BGR;15",
            "BGR;16",
            "BGR;24",
            "BGR;32",
        ]:
            with self.assertRaises(ValueError) as e:
                Image.new(mode, (1, 1))
            self.assertEqual(str(e.exception), "unrecognized image mode")

    def test_exception_inheritance(self):
        self.assertTrue(issubclass(UnidentifiedImageError, IOError))

    def test_sanity(self):

        im = Image.new("L", (100, 100))
        self.assertEqual(repr(im)[:45], "<PIL.Image.Image image mode=L size=100x100 at")
        self.assertEqual(im.mode, "L")
        self.assertEqual(im.size, (100, 100))

        im = Image.new("RGB", (100, 100))
        self.assertEqual(repr(im)[:45], "<PIL.Image.Image image mode=RGB size=100x100 ")
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (100, 100))

        Image.new("L", (100, 100), None)
        im2 = Image.new("L", (100, 100), 0)
        im3 = Image.new("L", (100, 100), "black")

        self.assertEqual(im2.getcolors(), [(10000, 0)])
        self.assertEqual(im3.getcolors(), [(10000, 0)])

        self.assertRaises(ValueError, Image.new, "X", (100, 100))
        self.assertRaises(ValueError, Image.new, "", (100, 100))
        # self.assertRaises(MemoryError, Image.new, "L", (1000000, 1000000))

    def test_width_height(self):
        im = Image.new("RGB", (1, 2))
        self.assertEqual(im.width, 1)
        self.assertEqual(im.height, 2)

        with self.assertRaises(AttributeError):
            im.size = (3, 4)

    def test_invalid_image(self):
        import io

        im = io.BytesIO(b"")
        self.assertRaises(UnidentifiedImageError, Image.open, im)

    def test_bad_mode(self):
        self.assertRaises(ValueError, Image.open, "filename", "bad mode")

    def test_stringio(self):
        self.assertRaises(ValueError, Image.open, io.StringIO())

    def test_pathlib(self):
        from PIL.Image import Path

        with Image.open(Path("Tests/images/multipage-mmap.tiff")) as im:
            self.assertEqual(im.mode, "P")
            self.assertEqual(im.size, (10, 10))

        with Image.open(Path("Tests/images/hopper.jpg")) as im:
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (128, 128))

            temp_file = self.tempfile("temp.jpg")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            im.save(Path(temp_file))

    def test_fp_name(self):
        temp_file = self.tempfile("temp.jpg")

        class FP:
            def write(a, b):
                pass

        fp = FP()
        fp.name = temp_file

        im = hopper()
        im.save(fp)

    def test_tempfile(self):
        # see #1460, pathlib support breaks tempfile.TemporaryFile on py27
        # Will error out on save on 3.0.0
        im = hopper()
        with tempfile.TemporaryFile() as fp:
            im.save(fp, "JPEG")
            fp.seek(0)
            with Image.open(fp) as reloaded:
                self.assert_image_similar(im, reloaded, 20)

    def test_unknown_extension(self):
        im = hopper()
        temp_file = self.tempfile("temp.unknown")
        self.assertRaises(ValueError, im.save, temp_file)

    def test_internals(self):
        im = Image.new("L", (100, 100))
        im.readonly = 1
        im._copy()
        self.assertFalse(im.readonly)

        im.readonly = 1
        im.paste(0, (0, 0, 100, 100))
        self.assertFalse(im.readonly)

    @unittest.skipIf(is_win32(), "Test requires opening tempfile twice")
    def test_readonly_save(self):
        temp_file = self.tempfile("temp.bmp")
        shutil.copy("Tests/images/rgb32bf-rgba.bmp", temp_file)

        with Image.open(temp_file) as im:
            self.assertTrue(im.readonly)
            im.save(temp_file)

    def test_dump(self):
        im = Image.new("L", (10, 10))
        im._dump(self.tempfile("temp_L.ppm"))

        im = Image.new("RGB", (10, 10))
        im._dump(self.tempfile("temp_RGB.ppm"))

        im = Image.new("HSV", (10, 10))
        self.assertRaises(ValueError, im._dump, self.tempfile("temp_HSV.ppm"))

    def test_comparison_with_other_type(self):
        # Arrange
        item = Image.new("RGB", (25, 25), "#000")
        num = 12

        # Act/Assert
        # Shouldn't cause AttributeError (#774)
        self.assertFalse(item is None)
        self.assertFalse(item == num)

    def test_expand_x(self):
        # Arrange
        im = hopper()
        orig_size = im.size
        xmargin = 5

        # Act
        im = im._expand(xmargin)

        # Assert
        self.assertEqual(im.size[0], orig_size[0] + 2 * xmargin)
        self.assertEqual(im.size[1], orig_size[1] + 2 * xmargin)

    def test_expand_xy(self):
        # Arrange
        im = hopper()
        orig_size = im.size
        xmargin = 5
        ymargin = 3

        # Act
        im = im._expand(xmargin, ymargin)

        # Assert
        self.assertEqual(im.size[0], orig_size[0] + 2 * xmargin)
        self.assertEqual(im.size[1], orig_size[1] + 2 * ymargin)

    def test_getbands(self):
        # Assert
        self.assertEqual(hopper("RGB").getbands(), ("R", "G", "B"))
        self.assertEqual(hopper("YCbCr").getbands(), ("Y", "Cb", "Cr"))

    def test_getchannel_wrong_params(self):
        im = hopper()

        self.assertRaises(ValueError, im.getchannel, -1)
        self.assertRaises(ValueError, im.getchannel, 3)
        self.assertRaises(ValueError, im.getchannel, "Z")
        self.assertRaises(ValueError, im.getchannel, "1")

    def test_getchannel(self):
        im = hopper("YCbCr")
        Y, Cb, Cr = im.split()

        self.assert_image_equal(Y, im.getchannel(0))
        self.assert_image_equal(Y, im.getchannel("Y"))
        self.assert_image_equal(Cb, im.getchannel(1))
        self.assert_image_equal(Cb, im.getchannel("Cb"))
        self.assert_image_equal(Cr, im.getchannel(2))
        self.assert_image_equal(Cr, im.getchannel("Cr"))

    def test_getbbox(self):
        # Arrange
        im = hopper()

        # Act
        bbox = im.getbbox()

        # Assert
        self.assertEqual(bbox, (0, 0, 128, 128))

    def test_ne(self):
        # Arrange
        im1 = Image.new("RGB", (25, 25), "black")
        im2 = Image.new("RGB", (25, 25), "white")

        # Act / Assert
        self.assertNotEqual(im1, im2)

    def test_alpha_composite(self):
        # https://stackoverflow.com/questions/3374878
        # Arrange
        from PIL import ImageDraw

        expected_colors = sorted(
            [
                (1122, (128, 127, 0, 255)),
                (1089, (0, 255, 0, 255)),
                (3300, (255, 0, 0, 255)),
                (1156, (170, 85, 0, 192)),
                (1122, (0, 255, 0, 128)),
                (1122, (255, 0, 0, 128)),
                (1089, (0, 255, 0, 0)),
            ]
        )

        dst = Image.new("RGBA", size=(100, 100), color=(0, 255, 0, 255))
        draw = ImageDraw.Draw(dst)
        draw.rectangle((0, 33, 100, 66), fill=(0, 255, 0, 128))
        draw.rectangle((0, 67, 100, 100), fill=(0, 255, 0, 0))
        src = Image.new("RGBA", size=(100, 100), color=(255, 0, 0, 255))
        draw = ImageDraw.Draw(src)
        draw.rectangle((33, 0, 66, 100), fill=(255, 0, 0, 128))
        draw.rectangle((67, 0, 100, 100), fill=(255, 0, 0, 0))

        # Act
        img = Image.alpha_composite(dst, src)

        # Assert
        img_colors = sorted(img.getcolors())
        self.assertEqual(img_colors, expected_colors)

    def test_alpha_inplace(self):
        src = Image.new("RGBA", (128, 128), "blue")

        over = Image.new("RGBA", (128, 128), "red")
        mask = hopper("L")
        over.putalpha(mask)

        target = Image.alpha_composite(src, over)

        # basic
        full = src.copy()
        full.alpha_composite(over)
        self.assert_image_equal(full, target)

        # with offset down to right
        offset = src.copy()
        offset.alpha_composite(over, (64, 64))
        self.assert_image_equal(
            offset.crop((64, 64, 127, 127)), target.crop((0, 0, 63, 63))
        )
        self.assertEqual(offset.size, (128, 128))

        # offset and crop
        box = src.copy()
        box.alpha_composite(over, (64, 64), (0, 0, 32, 32))
        self.assert_image_equal(box.crop((64, 64, 96, 96)), target.crop((0, 0, 32, 32)))
        self.assert_image_equal(box.crop((96, 96, 128, 128)), src.crop((0, 0, 32, 32)))
        self.assertEqual(box.size, (128, 128))

        # source point
        source = src.copy()
        source.alpha_composite(over, (32, 32), (32, 32, 96, 96))

        self.assert_image_equal(
            source.crop((32, 32, 96, 96)), target.crop((32, 32, 96, 96))
        )
        self.assertEqual(source.size, (128, 128))

        # errors
        self.assertRaises(ValueError, source.alpha_composite, over, "invalid source")
        self.assertRaises(
            ValueError, source.alpha_composite, over, (0, 0), "invalid destination"
        )
        self.assertRaises(ValueError, source.alpha_composite, over, 0)
        self.assertRaises(ValueError, source.alpha_composite, over, (0, 0), 0)
        self.assertRaises(ValueError, source.alpha_composite, over, (0, -1))
        self.assertRaises(ValueError, source.alpha_composite, over, (0, 0), (0, -1))

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
        with Image.open("Tests/images/rgb.jpg"):
            pass

        # Act
        extensions = Image.registered_extensions()

        # Assert
        self.assertTrue(extensions)
        for ext in [".cur", ".icns", ".tif", ".tiff"]:
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
        with Image.open("Tests/images/effect_mandelbrot.png") as im2:
            self.assert_image_equal(im, im2)

    def test_effect_mandelbrot_bad_arguments(self):
        # Arrange
        size = (512, 512)
        # Get coordinates the wrong way round:
        extent = (+3, +2.5, -2, -2.5)
        # Quality < 2:
        quality = 1

        # Act/Assert
        self.assertRaises(ValueError, Image.effect_mandelbrot, size, extent, quality)

    def test_effect_noise(self):
        # Arrange
        size = (100, 100)
        sigma = 128

        # Act
        im = Image.effect_noise(size, sigma)

        # Assert
        self.assertEqual(im.size, (100, 100))
        self.assertEqual(im.mode, "L")
        p0 = im.getpixel((0, 0))
        p1 = im.getpixel((0, 1))
        p2 = im.getpixel((0, 2))
        p3 = im.getpixel((0, 3))
        p4 = im.getpixel((0, 4))
        self.assert_not_all_same([p0, p1, p2, p3, p4])

    def test_effect_spread(self):
        # Arrange
        im = hopper()
        distance = 10

        # Act
        im2 = im.effect_spread(distance)

        # Assert
        self.assertEqual(im.size, (128, 128))
        with Image.open("Tests/images/effect_spread.png") as im3:
            self.assert_image_similar(im2, im3, 110)

    def test_check_size(self):
        # Checking that the _check_size function throws value errors
        # when we want it to.
        with self.assertRaises(ValueError):
            Image.new("RGB", 0)  # not a tuple
        with self.assertRaises(ValueError):
            Image.new("RGB", (0,))  # Tuple too short
        with self.assertRaises(ValueError):
            Image.new("RGB", (-1, -1))  # w,h < 0

        # this should pass with 0 sized images, #2259
        im = Image.new("L", (0, 0))
        self.assertEqual(im.size, (0, 0))

        im = Image.new("L", (0, 100))
        self.assertEqual(im.size, (0, 100))

        im = Image.new("L", (100, 0))
        self.assertEqual(im.size, (100, 0))

        self.assertTrue(Image.new("RGB", (1, 1)))
        # Should pass lists too
        i = Image.new("RGB", [1, 1])
        self.assertIsInstance(i.size, tuple)

    def test_storage_neg(self):
        # Storage.c accepted negative values for xsize, ysize.  Was
        # test_neg_ppm, but the core function for that has been
        # removed Calling directly into core to test the error in
        # Storage.c, rather than the size check above

        with self.assertRaises(ValueError):
            Image.core.fill("RGB", (2, -2), (0, 0, 0))

    def test_offset_not_implemented(self):
        # Arrange
        with hopper() as im:

            # Act / Assert
            self.assertRaises(NotImplementedError, im.offset, None)

    def test_fromstring(self):
        self.assertRaises(NotImplementedError, Image.fromstring)

    def test_linear_gradient_wrong_mode(self):
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        self.assertRaises(ValueError, Image.linear_gradient, wrong_mode)

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
            with Image.open(target_file) as target:
                target = target.convert(mode)
            self.assert_image_equal(im, target)

    def test_radial_gradient_wrong_mode(self):
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        self.assertRaises(ValueError, Image.radial_gradient, wrong_mode)

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
            with Image.open(target_file) as target:
                target = target.convert(mode)
            self.assert_image_equal(im, target)

    def test_register_extensions(self):
        test_format = "a"
        exts = ["b", "c"]
        for ext in exts:
            Image.register_extension(test_format, ext)
        ext_individual = Image.EXTENSION.copy()
        for ext in exts:
            del Image.EXTENSION[ext]

        Image.register_extensions(test_format, exts)
        ext_multiple = Image.EXTENSION.copy()
        for ext in exts:
            del Image.EXTENSION[ext]

        self.assertEqual(ext_individual, ext_multiple)

    def test_remap_palette(self):
        # Test illegal image mode
        with hopper() as im:
            self.assertRaises(ValueError, im.remap_palette, None)

    def test__new(self):
        from PIL import ImagePalette

        im = hopper("RGB")
        im_p = hopper("P")

        blank_p = Image.new("P", (10, 10))
        blank_pa = Image.new("PA", (10, 10))
        blank_p.palette = None
        blank_pa.palette = None

        def _make_new(base_image, im, palette_result=None):
            new_im = base_image._new(im)
            self.assertEqual(new_im.mode, im.mode)
            self.assertEqual(new_im.size, im.size)
            self.assertEqual(new_im.info, base_image.info)
            if palette_result is not None:
                self.assertEqual(new_im.palette.tobytes(), palette_result.tobytes())
            else:
                self.assertIsNone(new_im.palette)

        _make_new(im, im_p, im_p.palette)
        _make_new(im_p, im, None)
        _make_new(im, blank_p, ImagePalette.ImagePalette())
        _make_new(im, blank_pa, ImagePalette.ImagePalette())

    def test_p_from_rgb_rgba(self):
        for mode, color in [
            ("RGB", "#DDEEFF"),
            ("RGB", (221, 238, 255)),
            ("RGBA", (221, 238, 255, 255)),
        ]:
            im = Image.new("P", (100, 100), color)
            expected = Image.new(mode, (100, 100), color)
            self.assert_image_equal(im.convert(mode), expected)

    def test_no_resource_warning_on_save(self):
        # https://github.com/python-pillow/Pillow/issues/835
        # Arrange
        test_file = "Tests/images/hopper.png"
        temp_file = self.tempfile("temp.jpg")

        # Act/Assert
        with Image.open(test_file) as im:
            self.assert_warning(None, im.save, temp_file)

    def test_load_on_nonexclusive_multiframe(self):
        with open("Tests/images/frozenpond.mpo", "rb") as fp:

            def act(fp):
                im = Image.open(fp)
                im.load()

            act(fp)

            with Image.open(fp) as im:
                im.load()

            self.assertFalse(fp.closed)

    def test_overrun(self):
        for file in [
            "fli_overrun.bin",
            "sgi_overrun.bin",
            "sgi_overrun_expandrow.bin",
            "sgi_overrun_expandrow2.bin",
            "pcx_overrun.bin",
            "pcx_overrun2.bin",
        ]:
            with Image.open(os.path.join("Tests/images", file)) as im:
                try:
                    im.load()
                    self.assertFail()
                except OSError as e:
                    self.assertEqual(str(e), "buffer overrun when reading image file")

        with Image.open("Tests/images/fli_overrun2.bin") as im:
            try:
                im.seek(1)
                self.assertFail()
            except OSError as e:
                self.assertEqual(str(e), "buffer overrun when reading image file")


class MockEncoder:
    pass


def mock_encode(*args):
    encoder = MockEncoder()
    encoder.args = args
    return encoder


class TestRegistry(PillowTestCase):
    def test_encode_registry(self):

        Image.register_encoder("MOCK", mock_encode)
        self.assertIn("MOCK", Image.ENCODERS)

        enc = Image._getencoder("RGB", "MOCK", ("args",), extra=("extra",))

        self.assertIsInstance(enc, MockEncoder)
        self.assertEqual(enc.args, ("RGB", "args", "extra"))

    def test_encode_registry_fail(self):
        self.assertRaises(
            IOError,
            Image._getencoder,
            "RGB",
            "DoesNotExist",
            ("args",),
            extra=("extra",),
        )
