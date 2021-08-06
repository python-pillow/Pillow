import io
import os
import shutil
import sys
import tempfile

import pytest

import PIL
from PIL import Image, ImageDraw, ImagePalette, ImageShow, UnidentifiedImageError

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar_tofile,
    assert_not_all_same,
    hopper,
    is_win32,
    mark_if_feature_version,
    skip_unless_feature,
)


class TestImage:
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
            with pytest.raises(ValueError) as e:
                Image.new(mode, (1, 1))
            assert str(e.value) == "unrecognized image mode"

    def test_exception_inheritance(self):
        assert issubclass(UnidentifiedImageError, OSError)

    def test_sanity(self):

        im = Image.new("L", (100, 100))
        assert repr(im)[:45] == "<PIL.Image.Image image mode=L size=100x100 at"
        assert im.mode == "L"
        assert im.size == (100, 100)

        im = Image.new("RGB", (100, 100))
        assert repr(im)[:45] == "<PIL.Image.Image image mode=RGB size=100x100 "
        assert im.mode == "RGB"
        assert im.size == (100, 100)

        Image.new("L", (100, 100), None)
        im2 = Image.new("L", (100, 100), 0)
        im3 = Image.new("L", (100, 100), "black")

        assert im2.getcolors() == [(10000, 0)]
        assert im3.getcolors() == [(10000, 0)]

        with pytest.raises(ValueError):
            Image.new("X", (100, 100))
        with pytest.raises(ValueError):
            Image.new("", (100, 100))
        # with pytest.raises(MemoryError):
        #   Image.new("L", (1000000, 1000000))

    def test_open_formats(self):
        PNGFILE = "Tests/images/hopper.png"
        JPGFILE = "Tests/images/hopper.jpg"

        with pytest.raises(TypeError):
            with Image.open(PNGFILE, formats=123):
                pass

        for formats in [["JPEG"], ("JPEG",), ["jpeg"], ["Jpeg"], ["jPeG"], ["JpEg"]]:
            with pytest.raises(UnidentifiedImageError):
                with Image.open(PNGFILE, formats=formats):
                    pass

            with Image.open(JPGFILE, formats=formats) as im:
                assert im.mode == "RGB"
                assert im.size == (128, 128)

        for file in [PNGFILE, JPGFILE]:
            with Image.open(file, formats=None) as im:
                assert im.mode == "RGB"
                assert im.size == (128, 128)

    def test_width_height(self):
        im = Image.new("RGB", (1, 2))
        assert im.width == 1
        assert im.height == 2

        with pytest.raises(AttributeError):
            im.size = (3, 4)

    def test_invalid_image(self):
        import io

        im = io.BytesIO(b"")
        with pytest.raises(UnidentifiedImageError):
            with Image.open(im):
                pass

    def test_bad_mode(self):
        with pytest.raises(ValueError):
            with Image.open("filename", "bad mode"):
                pass

    def test_stringio(self):
        with pytest.raises(ValueError):
            with Image.open(io.StringIO()):
                pass

    def test_pathlib(self, tmp_path):
        from PIL.Image import Path

        with Image.open(Path("Tests/images/multipage-mmap.tiff")) as im:
            assert im.mode == "P"
            assert im.size == (10, 10)

        with Image.open(Path("Tests/images/hopper.jpg")) as im:
            assert im.mode == "RGB"
            assert im.size == (128, 128)

            for ext in (".jpg", ".jp2"):
                temp_file = str(tmp_path / ("temp." + ext))
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                im.save(Path(temp_file))

    def test_fp_name(self, tmp_path):
        temp_file = str(tmp_path / "temp.jpg")

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
            assert_image_similar_tofile(im, fp, 20)

    def test_unknown_extension(self, tmp_path):
        im = hopper()
        temp_file = str(tmp_path / "temp.unknown")
        with pytest.raises(ValueError):
            im.save(temp_file)

    def test_internals(self):
        im = Image.new("L", (100, 100))
        im.readonly = 1
        im._copy()
        assert not im.readonly

        im.readonly = 1
        im.paste(0, (0, 0, 100, 100))
        assert not im.readonly

    @pytest.mark.skipif(is_win32(), reason="Test requires opening tempfile twice")
    def test_readonly_save(self, tmp_path):
        temp_file = str(tmp_path / "temp.bmp")
        shutil.copy("Tests/images/rgb32bf-rgba.bmp", temp_file)

        with Image.open(temp_file) as im:
            assert im.readonly
            im.save(temp_file)

    def test_dump(self, tmp_path):
        im = Image.new("L", (10, 10))
        im._dump(str(tmp_path / "temp_L.ppm"))

        im = Image.new("RGB", (10, 10))
        im._dump(str(tmp_path / "temp_RGB.ppm"))

        im = Image.new("HSV", (10, 10))
        with pytest.raises(ValueError):
            im._dump(str(tmp_path / "temp_HSV.ppm"))

    def test_comparison_with_other_type(self):
        # Arrange
        item = Image.new("RGB", (25, 25), "#000")
        num = 12

        # Act/Assert
        # Shouldn't cause AttributeError (#774)
        assert item is not None
        assert item != num

    def test_expand_x(self):
        # Arrange
        im = hopper()
        orig_size = im.size
        xmargin = 5

        # Act
        im = im._expand(xmargin)

        # Assert
        assert im.size[0] == orig_size[0] + 2 * xmargin
        assert im.size[1] == orig_size[1] + 2 * xmargin

    def test_expand_xy(self):
        # Arrange
        im = hopper()
        orig_size = im.size
        xmargin = 5
        ymargin = 3

        # Act
        im = im._expand(xmargin, ymargin)

        # Assert
        assert im.size[0] == orig_size[0] + 2 * xmargin
        assert im.size[1] == orig_size[1] + 2 * ymargin

    def test_getbands(self):
        # Assert
        assert hopper("RGB").getbands() == ("R", "G", "B")
        assert hopper("YCbCr").getbands() == ("Y", "Cb", "Cr")

    def test_getchannel_wrong_params(self):
        im = hopper()

        with pytest.raises(ValueError):
            im.getchannel(-1)
        with pytest.raises(ValueError):
            im.getchannel(3)
        with pytest.raises(ValueError):
            im.getchannel("Z")
        with pytest.raises(ValueError):
            im.getchannel("1")

    def test_getchannel(self):
        im = hopper("YCbCr")
        Y, Cb, Cr = im.split()

        assert_image_equal(Y, im.getchannel(0))
        assert_image_equal(Y, im.getchannel("Y"))
        assert_image_equal(Cb, im.getchannel(1))
        assert_image_equal(Cb, im.getchannel("Cb"))
        assert_image_equal(Cr, im.getchannel(2))
        assert_image_equal(Cr, im.getchannel("Cr"))

    def test_getbbox(self):
        # Arrange
        im = hopper()

        # Act
        bbox = im.getbbox()

        # Assert
        assert bbox == (0, 0, 128, 128)

    def test_ne(self):
        # Arrange
        im1 = Image.new("RGB", (25, 25), "black")
        im2 = Image.new("RGB", (25, 25), "white")

        # Act / Assert
        assert im1 != im2

    def test_alpha_composite(self):
        # https://stackoverflow.com/questions/3374878
        # Arrange
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
        assert img_colors == expected_colors

    def test_alpha_inplace(self):
        src = Image.new("RGBA", (128, 128), "blue")

        over = Image.new("RGBA", (128, 128), "red")
        mask = hopper("L")
        over.putalpha(mask)

        target = Image.alpha_composite(src, over)

        # basic
        full = src.copy()
        full.alpha_composite(over)
        assert_image_equal(full, target)

        # with offset down to right
        offset = src.copy()
        offset.alpha_composite(over, (64, 64))
        assert_image_equal(offset.crop((64, 64, 127, 127)), target.crop((0, 0, 63, 63)))
        assert offset.size == (128, 128)

        # with negative offset
        offset = src.copy()
        offset.alpha_composite(over, (-64, -64))
        assert_image_equal(offset.crop((0, 0, 63, 63)), target.crop((64, 64, 127, 127)))
        assert offset.size == (128, 128)

        # offset and crop
        box = src.copy()
        box.alpha_composite(over, (64, 64), (0, 0, 32, 32))
        assert_image_equal(box.crop((64, 64, 96, 96)), target.crop((0, 0, 32, 32)))
        assert_image_equal(box.crop((96, 96, 128, 128)), src.crop((0, 0, 32, 32)))
        assert box.size == (128, 128)

        # source point
        source = src.copy()
        source.alpha_composite(over, (32, 32), (32, 32, 96, 96))

        assert_image_equal(source.crop((32, 32, 96, 96)), target.crop((32, 32, 96, 96)))
        assert source.size == (128, 128)

        # errors
        with pytest.raises(ValueError):
            source.alpha_composite(over, "invalid source")
        with pytest.raises(ValueError):
            source.alpha_composite(over, (0, 0), "invalid destination")
        with pytest.raises(ValueError):
            source.alpha_composite(over, 0)
        with pytest.raises(ValueError):
            source.alpha_composite(over, (0, 0), 0)
        with pytest.raises(ValueError):
            source.alpha_composite(over, (0, 0), (0, -1))

    def test_registered_extensions_uninitialized(self):
        # Arrange
        Image._initialized = 0
        extension = Image.EXTENSION
        Image.EXTENSION = {}

        # Act
        Image.registered_extensions()

        # Assert
        assert Image._initialized == 2

        # Restore the original state and assert
        Image.EXTENSION = extension
        assert Image.EXTENSION

    def test_registered_extensions(self):
        # Arrange
        # Open an image to trigger plugin registration
        with Image.open("Tests/images/rgb.jpg"):
            pass

        # Act
        extensions = Image.registered_extensions()

        # Assert
        assert extensions
        for ext in [".cur", ".icns", ".tif", ".tiff"]:
            assert ext in extensions

    def test_effect_mandelbrot(self):
        # Arrange
        size = (512, 512)
        extent = (-3, -2.5, 2, 2.5)
        quality = 100

        # Act
        im = Image.effect_mandelbrot(size, extent, quality)

        # Assert
        assert im.size == (512, 512)
        assert_image_equal_tofile(im, "Tests/images/effect_mandelbrot.png")

    def test_effect_mandelbrot_bad_arguments(self):
        # Arrange
        size = (512, 512)
        # Get coordinates the wrong way round:
        extent = (+3, +2.5, -2, -2.5)
        # Quality < 2:
        quality = 1

        # Act/Assert
        with pytest.raises(ValueError):
            Image.effect_mandelbrot(size, extent, quality)

    def test_effect_noise(self):
        # Arrange
        size = (100, 100)
        sigma = 128

        # Act
        im = Image.effect_noise(size, sigma)

        # Assert
        assert im.size == (100, 100)
        assert im.mode == "L"
        p0 = im.getpixel((0, 0))
        p1 = im.getpixel((0, 1))
        p2 = im.getpixel((0, 2))
        p3 = im.getpixel((0, 3))
        p4 = im.getpixel((0, 4))
        assert_not_all_same([p0, p1, p2, p3, p4])

    def test_effect_spread(self):
        # Arrange
        im = hopper()
        distance = 10

        # Act
        im2 = im.effect_spread(distance)

        # Assert
        assert im.size == (128, 128)
        assert_image_similar_tofile(im2, "Tests/images/effect_spread.png", 110)

    def test_effect_spread_zero(self):
        # Arrange
        im = hopper()
        distance = 0

        # Act
        im2 = im.effect_spread(distance)

        # Assert
        assert_image_equal(im, im2)

    def test_check_size(self):
        # Checking that the _check_size function throws value errors when we want it to
        with pytest.raises(ValueError):
            Image.new("RGB", 0)  # not a tuple
        with pytest.raises(ValueError):
            Image.new("RGB", (0,))  # Tuple too short
        with pytest.raises(ValueError):
            Image.new("RGB", (-1, -1))  # w,h < 0

        # this should pass with 0 sized images, #2259
        im = Image.new("L", (0, 0))
        assert im.size == (0, 0)

        im = Image.new("L", (0, 100))
        assert im.size == (0, 100)

        im = Image.new("L", (100, 0))
        assert im.size == (100, 0)

        assert Image.new("RGB", (1, 1))
        # Should pass lists too
        i = Image.new("RGB", [1, 1])
        assert isinstance(i.size, tuple)

    def test_storage_neg(self):
        # Storage.c accepted negative values for xsize, ysize.  Was
        # test_neg_ppm, but the core function for that has been
        # removed Calling directly into core to test the error in
        # Storage.c, rather than the size check above

        with pytest.raises(ValueError):
            Image.core.fill("RGB", (2, -2), (0, 0, 0))

    def test_one_item_tuple(self):
        for mode in ("I", "F", "L"):
            im = Image.new(mode, (100, 100), (5,))
            px = im.load()
            assert px[0, 0] == 5

    def test_linear_gradient_wrong_mode(self):
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        with pytest.raises(ValueError):
            Image.linear_gradient(wrong_mode)

    def test_linear_gradient(self):

        # Arrange
        target_file = "Tests/images/linear_gradient.png"
        for mode in ["L", "P", "I", "F"]:

            # Act
            im = Image.linear_gradient(mode)

            # Assert
            assert im.size == (256, 256)
            assert im.mode == mode
            assert im.getpixel((0, 0)) == 0
            assert im.getpixel((255, 255)) == 255
            with Image.open(target_file) as target:
                target = target.convert(mode)
            assert_image_equal(im, target)

    def test_radial_gradient_wrong_mode(self):
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        with pytest.raises(ValueError):
            Image.radial_gradient(wrong_mode)

    def test_radial_gradient(self):

        # Arrange
        target_file = "Tests/images/radial_gradient.png"
        for mode in ["L", "P", "I", "F"]:

            # Act
            im = Image.radial_gradient(mode)

            # Assert
            assert im.size == (256, 256)
            assert im.mode == mode
            assert im.getpixel((0, 0)) == 255
            assert im.getpixel((128, 128)) == 0
            with Image.open(target_file) as target:
                target = target.convert(mode)
            assert_image_equal(im, target)

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

        assert ext_individual == ext_multiple

    def test_remap_palette(self):
        # Test identity transform
        with Image.open("Tests/images/hopper.gif") as im:
            assert_image_equal(im, im.remap_palette(list(range(256))))

        # Test illegal image mode
        with hopper() as im:
            with pytest.raises(ValueError):
                im.remap_palette(None)

    def test__new(self):
        im = hopper("RGB")
        im_p = hopper("P")

        blank_p = Image.new("P", (10, 10))
        blank_pa = Image.new("PA", (10, 10))
        blank_p.palette = None
        blank_pa.palette = None

        def _make_new(base_image, im, palette_result=None):
            new_im = base_image._new(im)
            assert new_im.mode == im.mode
            assert new_im.size == im.size
            assert new_im.info == base_image.info
            if palette_result is not None:
                assert new_im.palette.tobytes() == palette_result.tobytes()
            else:
                assert new_im.palette is None

        _make_new(im, im_p, ImagePalette.ImagePalette(list(range(256)) * 3))
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
            assert_image_equal(im.convert(mode), expected)

    def test_showxv_deprecation(self):
        class TestViewer(ImageShow.Viewer):
            def show_image(self, image, **options):
                return True

        viewer = TestViewer()
        ImageShow.register(viewer, -1)

        im = Image.new("RGB", (50, 50), "white")

        with pytest.warns(DeprecationWarning):
            Image._showxv(im)

        # Restore original state
        ImageShow._viewers.pop(0)

    def test_no_resource_warning_on_save(self, tmp_path):
        # https://github.com/python-pillow/Pillow/issues/835
        # Arrange
        test_file = "Tests/images/hopper.png"
        temp_file = str(tmp_path / "temp.jpg")

        # Act/Assert
        with Image.open(test_file) as im:
            with pytest.warns(None) as record:
                im.save(temp_file)
            assert not record

    def test_load_on_nonexclusive_multiframe(self):
        with open("Tests/images/frozenpond.mpo", "rb") as fp:

            def act(fp):
                im = Image.open(fp)
                im.load()

            act(fp)

            with Image.open(fp) as im:
                im.load()

            assert not fp.closed

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_exif_jpeg(self, tmp_path):
        with Image.open("Tests/images/exif-72dpi-int.jpg") as im:  # Little endian
            exif = im.getexif()
            assert 258 not in exif
            assert 274 in exif
            assert 282 in exif
            assert exif[296] == 2
            assert exif[11] == "gThumb 3.0.1"

            out = str(tmp_path / "temp.jpg")
            exif[258] = 8
            del exif[274]
            del exif[282]
            exif[296] = 455
            exif[11] = "Pillow test"
            im.save(out, exif=exif)
        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            assert reloaded_exif[258] == 8
            assert 274 not in reloaded_exif
            assert 282 not in reloaded_exif
            assert reloaded_exif[296] == 455
            assert reloaded_exif[11] == "Pillow test"

        with Image.open("Tests/images/no-dpi-in-exif.jpg") as im:  # Big endian
            exif = im.getexif()
            assert 258 not in exif
            assert 306 in exif
            assert exif[274] == 1
            assert exif[305] == "Adobe Photoshop CC 2017 (Macintosh)"

            out = str(tmp_path / "temp.jpg")
            exif[258] = 8
            del exif[306]
            exif[274] = 455
            exif[305] = "Pillow test"
            im.save(out, exif=exif)
        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            assert reloaded_exif[258] == 8
            assert 306 not in reloaded_exif
            assert reloaded_exif[274] == 455
            assert reloaded_exif[305] == "Pillow test"

    @skip_unless_feature("webp")
    @skip_unless_feature("webp_anim")
    def test_exif_webp(self, tmp_path):
        with Image.open("Tests/images/hopper.webp") as im:
            exif = im.getexif()
            assert exif == {}

            out = str(tmp_path / "temp.webp")
            exif[258] = 8
            exif[40963] = 455
            exif[305] = "Pillow test"

            def check_exif():
                with Image.open(out) as reloaded:
                    reloaded_exif = reloaded.getexif()
                    assert reloaded_exif[258] == 8
                    assert reloaded_exif[40963] == 455
                    assert reloaded_exif[305] == "Pillow test"

            im.save(out, exif=exif)
            check_exif()
            im.save(out, exif=exif, save_all=True)
            check_exif()

    def test_exif_png(self, tmp_path):
        with Image.open("Tests/images/exif.png") as im:
            exif = im.getexif()
            assert exif == {274: 1}

            out = str(tmp_path / "temp.png")
            exif[258] = 8
            del exif[274]
            exif[40963] = 455
            exif[305] = "Pillow test"
            im.save(out, exif=exif)

        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            assert reloaded_exif == {258: 8, 40963: 455, 305: "Pillow test"}

    def test_exif_interop(self):
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()
            assert exif.get_ifd(0xA005) == {
                1: "R98",
                2: b"0100",
                4097: 2272,
                4098: 1704,
            }

            reloaded_exif = Image.Exif()
            reloaded_exif.load(exif.tobytes())
            assert reloaded_exif.get_ifd(0xA005) == exif.get_ifd(0xA005)

    def test_exif_ifd(self):
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()
        del exif.get_ifd(0x8769)[0xA005]

        reloaded_exif = Image.Exif()
        reloaded_exif.load(exif.tobytes())
        assert reloaded_exif.get_ifd(0x8769) == exif.get_ifd(0x8769)

    def test_exif_load_from_fp(self):
        with Image.open("Tests/images/flower.jpg") as im:
            data = im.info["exif"]
            if data.startswith(b"Exif\x00\x00"):
                data = data[6:]
            fp = io.BytesIO(data)

            exif = Image.Exif()
            exif.load_from_fp(fp)
            assert exif == {
                271: "Canon",
                272: "Canon PowerShot S40",
                274: 1,
                282: 180.0,
                283: 180.0,
                296: 2,
                306: "2003:12:14 12:01:44",
                531: 1,
                34665: 196,
            }

    @pytest.mark.skipif(
        sys.version_info < (3, 7), reason="Python 3.7 or greater required"
    )
    def test_categories_deprecation(self):
        with pytest.warns(DeprecationWarning):
            assert hopper().category == 0

        with pytest.warns(DeprecationWarning):
            assert Image.NORMAL == 0
        with pytest.warns(DeprecationWarning):
            assert Image.SEQUENCE == 1
        with pytest.warns(DeprecationWarning):
            assert Image.CONTAINER == 2

    @pytest.mark.parametrize(
        "test_module",
        [PIL, Image],
    )
    def test_pillow_version(self, test_module):
        with pytest.warns(DeprecationWarning):
            assert test_module.PILLOW_VERSION == PIL.__version__

        with pytest.warns(DeprecationWarning):
            str(test_module.PILLOW_VERSION)

        with pytest.warns(DeprecationWarning):
            assert int(test_module.PILLOW_VERSION[0]) >= 7

        with pytest.warns(DeprecationWarning):
            assert test_module.PILLOW_VERSION < "9.9.0"

        with pytest.warns(DeprecationWarning):
            assert test_module.PILLOW_VERSION <= "9.9.0"

        with pytest.warns(DeprecationWarning):
            assert test_module.PILLOW_VERSION != "7.0.0"

        with pytest.warns(DeprecationWarning):
            assert test_module.PILLOW_VERSION >= "7.0.0"

        with pytest.warns(DeprecationWarning):
            assert test_module.PILLOW_VERSION > "7.0.0"

    @pytest.mark.parametrize(
        "path",
        [
            "fli_overrun.bin",
            "sgi_overrun.bin",
            "sgi_overrun_expandrow.bin",
            "sgi_overrun_expandrow2.bin",
            "pcx_overrun.bin",
            "pcx_overrun2.bin",
            "ossfuzz-4836216264589312.pcx",
            "01r_00.pcx",
        ],
    )
    def test_overrun(self, path):
        """For overrun completeness, test as:
        valgrind pytest -qq Tests/test_image.py::TestImage::test_overrun | grep decode.c
        """
        with Image.open(os.path.join("Tests/images", path)) as im:
            try:
                im.load()
                assert False
            except OSError as e:
                buffer_overrun = str(e) == "buffer overrun when reading image file"
                truncated = "image file is truncated" in str(e)

                assert buffer_overrun or truncated

    def test_fli_overrun2(self):
        with Image.open("Tests/images/fli_overrun2.bin") as im:
            try:
                im.seek(1)
                assert False
            except OSError as e:
                assert str(e) == "buffer overrun when reading image file"

    def test_show_deprecation(self, monkeypatch):
        monkeypatch.setattr(Image, "_show", lambda *args, **kwargs: None)

        im = Image.new("RGB", (50, 50), "white")

        with pytest.warns(None) as raised:
            im.show()
        assert not raised

        with pytest.warns(DeprecationWarning):
            im.show(command="mock")


class MockEncoder:
    pass


def mock_encode(*args):
    encoder = MockEncoder()
    encoder.args = args
    return encoder


class TestRegistry:
    def test_encode_registry(self):

        Image.register_encoder("MOCK", mock_encode)
        assert "MOCK" in Image.ENCODERS

        enc = Image._getencoder("RGB", "MOCK", ("args",), extra=("extra",))

        assert isinstance(enc, MockEncoder)
        assert enc.args == ("RGB", "args", "extra")

    def test_encode_registry_fail(self):
        with pytest.raises(OSError):
            Image._getencoder("RGB", "DoesNotExist", ("args",), extra=("extra",))
