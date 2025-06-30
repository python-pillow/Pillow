from __future__ import annotations

import io
import logging
import os
import shutil
import sys
import tempfile
import warnings
from pathlib import Path
from types import ModuleType
from typing import IO, Any

import pytest

from PIL import (
    ExifTags,
    Image,
    ImageDraw,
    ImageFile,
    ImagePalette,
    UnidentifiedImageError,
    features,
)

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    assert_not_all_same,
    hopper,
    is_big_endian,
    is_win32,
    mark_if_feature_version,
    skip_unless_feature,
    timeout_unless_slower_valgrind,
)

ElementTree: ModuleType | None
try:
    from defusedxml import ElementTree
except ImportError:
    ElementTree = None

PrettyPrinter: type | None
try:
    from IPython.lib.pretty import PrettyPrinter
except ImportError:
    PrettyPrinter = None


# Deprecation helper
def helper_image_new(mode: str, size: tuple[int, int]) -> Image.Image:
    if mode.startswith("BGR;"):
        with pytest.warns(DeprecationWarning, match="BGR;"):
            return Image.new(mode, size)
    else:
        return Image.new(mode, size)


class TestImage:
    @pytest.mark.parametrize("mode", Image.MODES + ["BGR;15", "BGR;16", "BGR;24"])
    def test_image_modes_success(self, mode: str) -> None:
        helper_image_new(mode, (1, 1))

    @pytest.mark.parametrize("mode", ("", "bad", "very very long"))
    def test_image_modes_fail(self, mode: str) -> None:
        with pytest.raises(ValueError, match="unrecognized image mode"):
            Image.new(mode, (1, 1))

    def test_exception_inheritance(self) -> None:
        assert issubclass(UnidentifiedImageError, OSError)

    def test_sanity(self) -> None:
        im = Image.new("L", (100, 100))
        assert repr(im).startswith("<PIL.Image.Image image mode=L size=100x100 at")
        assert im.mode == "L"
        assert im.size == (100, 100)

        im = Image.new("RGB", (100, 100))
        assert repr(im).startswith("<PIL.Image.Image image mode=RGB size=100x100 ")
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

    @pytest.mark.skipif(PrettyPrinter is None, reason="IPython is not installed")
    def test_repr_pretty(self) -> None:
        im = Image.new("L", (100, 100))

        output = io.StringIO()
        assert PrettyPrinter is not None
        p = PrettyPrinter(output)
        im._repr_pretty_(p, False)
        assert output.getvalue() == "<PIL.Image.Image image mode=L size=100x100>"

    def test_open_formats(self) -> None:
        PNGFILE = "Tests/images/hopper.png"
        JPGFILE = "Tests/images/hopper.jpg"

        with pytest.raises(TypeError):
            with Image.open(PNGFILE, formats=123):  # type: ignore[arg-type]
                pass

        format_list: list[list[str] | tuple[str, ...]] = [
            ["JPEG"],
            ("JPEG",),
            ["jpeg"],
            ["Jpeg"],
            ["jPeG"],
            ["JpEg"],
        ]
        for formats in format_list:
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

    def test_open_verbose_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(Image, "WARN_POSSIBLE_FORMATS", True)

        im = io.BytesIO(b"")
        with pytest.raises(UnidentifiedImageError):
            with pytest.warns(UserWarning, match="opening failed"):
                with Image.open(im):
                    pass

    def test_width_height(self) -> None:
        im = Image.new("RGB", (1, 2))
        assert im.width == 1
        assert im.height == 2

        with pytest.raises(AttributeError):
            im.size = (3, 4)  # type: ignore[misc]

    def test_set_mode(self) -> None:
        im = Image.new("RGB", (1, 1))

        with pytest.raises(AttributeError):
            im.mode = "P"  # type: ignore[misc]

    def test_empty_path(self) -> None:
        with pytest.raises(FileNotFoundError):
            Image.open("")

    def test_invalid_image(self) -> None:
        im = io.BytesIO(b"")
        with pytest.raises(UnidentifiedImageError):
            with Image.open(im):
                pass

    def test_bad_mode(self) -> None:
        with pytest.raises(ValueError):
            with Image.open("filename", "bad mode"):  # type: ignore[arg-type]
                pass

    def test_stringio(self) -> None:
        with pytest.raises(ValueError):
            with Image.open(io.StringIO()):  # type: ignore[arg-type]
                pass

    def test_string(self, tmp_path: Path) -> None:
        out = str(tmp_path / "temp.png")
        im = hopper()
        im.save(out)
        with Image.open(out) as reloaded:
            assert_image_equal(im, reloaded)

    def test_pathlib(self, tmp_path: Path) -> None:
        with Image.open(Path("Tests/images/multipage-mmap.tiff")) as im:
            assert im.mode == "P"
            assert im.size == (10, 10)

        with Image.open(Path("Tests/images/hopper.jpg")) as im:
            assert im.mode == "RGB"
            assert im.size == (128, 128)

            for ext in (".jpg", ".jp2"):
                if ext == ".jp2" and not features.check_codec("jpg_2000"):
                    pytest.skip("jpg_2000 not available")
                im.save(tmp_path / ("temp." + ext))

    def test_fp_name(self, tmp_path: Path) -> None:
        temp_file = tmp_path / "temp.jpg"

        class FP(io.BytesIO):
            name: Path

            if sys.version_info >= (3, 12):
                from collections.abc import Buffer

                def write(self, data: Buffer) -> int:
                    return len(data)

            else:

                def write(self, data: Any) -> int:
                    return len(data)

        fp = FP()
        fp.name = temp_file

        im = hopper()
        im.save(fp)

    def test_tempfile(self) -> None:
        # see #1460, pathlib support breaks tempfile.TemporaryFile on py27
        # Will error out on save on 3.0.0
        im = hopper()
        with tempfile.TemporaryFile() as fp:
            im.save(fp, "JPEG")
            fp.seek(0)
            with Image.open(fp) as reloaded:
                assert_image_similar(im, reloaded, 20)

    def test_unknown_extension(self, tmp_path: Path) -> None:
        temp_file = tmp_path / "temp.unknown"
        with hopper() as im:
            with pytest.raises(ValueError):
                im.save(temp_file)

    def test_internals(self) -> None:
        im = Image.new("L", (100, 100))
        im.readonly = 1
        im._copy()
        assert not im.readonly

        im.readonly = 1
        im.paste(0, (0, 0, 100, 100))
        assert not im.readonly

    @pytest.mark.skipif(is_win32(), reason="Test requires opening tempfile twice")
    @pytest.mark.skipif(
        sys.platform == "cygwin",
        reason="Test requires opening an mmaped file for writing",
    )
    def test_readonly_save(self, tmp_path: Path) -> None:
        temp_file = tmp_path / "temp.bmp"
        shutil.copy("Tests/images/rgb32bf-rgba.bmp", temp_file)

        with Image.open(temp_file) as im:
            assert im.readonly
            im.save(temp_file)

    def test_save_without_changing_readonly(self, tmp_path: Path) -> None:
        temp_file = tmp_path / "temp.bmp"

        with Image.open("Tests/images/rgb32bf-rgba.bmp") as im:
            assert im.readonly

            im.save(temp_file)
            assert im.readonly

    def test_dump(self, tmp_path: Path) -> None:
        im = Image.new("L", (10, 10))
        im._dump(str(tmp_path / "temp_L.ppm"))

        im = Image.new("RGB", (10, 10))
        im._dump(str(tmp_path / "temp_RGB.ppm"))

        im = Image.new("HSV", (10, 10))
        with pytest.raises(ValueError):
            im._dump(str(tmp_path / "temp_HSV.ppm"))

    def test_comparison_with_other_type(self) -> None:
        # Arrange
        item = Image.new("RGB", (25, 25), "#000")
        num = 12

        # Act/Assert
        # Shouldn't cause AttributeError (#774)
        assert item is not None
        assert item != num

    def test_expand_x(self) -> None:
        # Arrange
        im = hopper()
        orig_size = im.size
        xmargin = 5

        # Act
        im = im._expand(xmargin)

        # Assert
        assert im.size[0] == orig_size[0] + 2 * xmargin
        assert im.size[1] == orig_size[1] + 2 * xmargin

    def test_expand_xy(self) -> None:
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

    def test_getbands(self) -> None:
        # Assert
        assert hopper("RGB").getbands() == ("R", "G", "B")
        assert hopper("YCbCr").getbands() == ("Y", "Cb", "Cr")

    def test_getchannel_wrong_params(self) -> None:
        im = hopper()

        with pytest.raises(ValueError):
            im.getchannel(-1)
        with pytest.raises(ValueError):
            im.getchannel(3)
        with pytest.raises(ValueError):
            im.getchannel("Z")
        with pytest.raises(ValueError):
            im.getchannel("1")

    def test_getchannel(self) -> None:
        im = hopper("YCbCr")
        Y, Cb, Cr = im.split()

        assert_image_equal(Y, im.getchannel(0))
        assert_image_equal(Y, im.getchannel("Y"))
        assert_image_equal(Cb, im.getchannel(1))
        assert_image_equal(Cb, im.getchannel("Cb"))
        assert_image_equal(Cr, im.getchannel(2))
        assert_image_equal(Cr, im.getchannel("Cr"))

    def test_getbbox(self) -> None:
        # Arrange
        im = hopper()

        # Act
        bbox = im.getbbox()

        # Assert
        assert bbox == (0, 0, 128, 128)

    def test_ne(self) -> None:
        # Arrange
        im1 = Image.new("RGB", (25, 25), "black")
        im2 = Image.new("RGB", (25, 25), "white")

        # Act / Assert
        assert im1 != im2

    def test_alpha_composite(self) -> None:
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
        img_colors = img.getcolors()
        assert img_colors is not None
        assert sorted(img_colors) == expected_colors

    def test_alpha_inplace(self) -> None:
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
            source.alpha_composite(over, "invalid destination")  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            source.alpha_composite(over, (0, 0), "invalid source")  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            source.alpha_composite(over, 0)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            source.alpha_composite(over, (0, 0), 0)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            source.alpha_composite(over, (0, 0), (0, -1))

    def test_register_open_duplicates(self) -> None:
        # Arrange
        factory, accept = Image.OPEN["JPEG"]
        id_length = len(Image.ID)

        # Act
        Image.register_open("JPEG", factory, accept)

        # Assert
        assert len(Image.ID) == id_length

    def test_registered_extensions_uninitialized(self) -> None:
        # Arrange
        Image._initialized = 0

        # Act
        Image.registered_extensions()

        # Assert
        assert Image._initialized == 2

    def test_registered_extensions(self) -> None:
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

    def test_effect_mandelbrot(self) -> None:
        # Arrange
        size = (512, 512)
        extent = (-3, -2.5, 2, 2.5)
        quality = 100

        # Act
        im = Image.effect_mandelbrot(size, extent, quality)

        # Assert
        assert im.size == (512, 512)
        assert_image_equal_tofile(im, "Tests/images/effect_mandelbrot.png")

    def test_effect_mandelbrot_bad_arguments(self) -> None:
        # Arrange
        size = (512, 512)
        # Get coordinates the wrong way round:
        extent = (+3, +2.5, -2, -2.5)
        # Quality < 2:
        quality = 1

        # Act/Assert
        with pytest.raises(ValueError):
            Image.effect_mandelbrot(size, extent, quality)

    def test_effect_noise(self) -> None:
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

    def test_effect_spread(self) -> None:
        # Arrange
        im = hopper()
        distance = 10

        # Act
        im2 = im.effect_spread(distance)

        # Assert
        assert im.size == (128, 128)
        assert_image_similar_tofile(im2, "Tests/images/effect_spread.png", 110)

    def test_effect_spread_zero(self) -> None:
        # Arrange
        im = hopper()
        distance = 0

        # Act
        im2 = im.effect_spread(distance)

        # Assert
        assert_image_equal(im, im2)

    def test_check_size(self) -> None:
        # Checking that the _check_size function throws value errors when we want it to
        with pytest.raises(ValueError):
            # not a tuple
            Image.new("RGB", 0)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            # tuple too short
            Image.new("RGB", (0,))  # type: ignore[arg-type]
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

    @timeout_unless_slower_valgrind(0.75)
    @pytest.mark.parametrize("size", ((0, 100000000), (100000000, 0)))
    def test_empty_image(self, size: tuple[int, int]) -> None:
        Image.new("RGB", size)

    def test_storage_neg(self) -> None:
        # Storage.c accepted negative values for xsize, ysize.  Was
        # test_neg_ppm, but the core function for that has been
        # removed Calling directly into core to test the error in
        # Storage.c, rather than the size check above

        with pytest.raises(ValueError):
            Image.core.fill("RGB", (2, -2), (0, 0, 0))

    def test_one_item_tuple(self) -> None:
        for mode in ("I", "F", "L"):
            im = Image.new(mode, (100, 100), (5,))
            assert im.getpixel((0, 0)) == 5

    def test_linear_gradient_wrong_mode(self) -> None:
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        with pytest.raises(ValueError):
            Image.linear_gradient(wrong_mode)

    @pytest.mark.parametrize("mode", ("L", "P", "I", "F"))
    def test_linear_gradient(self, mode: str) -> None:
        # Arrange
        target_file = "Tests/images/linear_gradient.png"

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

    def test_radial_gradient_wrong_mode(self) -> None:
        # Arrange
        wrong_mode = "RGB"

        # Act / Assert
        with pytest.raises(ValueError):
            Image.radial_gradient(wrong_mode)

    @pytest.mark.parametrize("mode", ("L", "P", "I", "F"))
    def test_radial_gradient(self, mode: str) -> None:
        # Arrange
        target_file = "Tests/images/radial_gradient.png"

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

    def test_register_extensions(self) -> None:
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

    def test_remap_palette(self) -> None:
        # Test identity transform
        with Image.open("Tests/images/hopper.gif") as im:
            assert_image_equal(im, im.remap_palette(list(range(256))))

        # Test identity transform with an RGBA palette
        im = Image.new("P", (256, 1))
        for x in range(256):
            im.putpixel((x, 0), x)
        im.putpalette(list(range(256)) * 4, "RGBA")
        im_remapped = im.remap_palette(list(range(256)))
        assert_image_equal(im, im_remapped)
        assert im.palette is not None
        assert im_remapped.palette is not None
        assert im.palette.palette == im_remapped.palette.palette

        # Test illegal image mode
        with hopper() as im:
            with pytest.raises(ValueError):
                im.remap_palette([])

    def test_remap_palette_transparency(self) -> None:
        im = Image.new("P", (1, 2), (0, 0, 0))
        im.putpixel((0, 1), (255, 0, 0))
        im.info["transparency"] = 0

        im_remapped = im.remap_palette([1, 0])
        assert im_remapped.info["transparency"] == 1
        palette = im_remapped.getpalette()
        assert palette is not None
        assert len(palette) == 6

        # Test unused transparency
        im.info["transparency"] = 2

        im_remapped = im.remap_palette([1, 0])
        assert "transparency" not in im_remapped.info

    def test__new(self) -> None:
        im = hopper("RGB")
        im_p = hopper("P")

        blank_p = Image.new("P", (10, 10))
        blank_pa = Image.new("PA", (10, 10))
        blank_p.palette = None
        blank_pa.palette = None

        def _make_new(
            base_image: Image.Image,
            image: Image.Image,
            palette_result: ImagePalette.ImagePalette | None = None,
        ) -> None:
            new_image = base_image._new(image.im)
            assert new_image.mode == image.mode
            assert new_image.size == image.size
            assert new_image.info == base_image.info
            if palette_result is not None:
                assert new_image.palette is not None
                assert new_image.palette.tobytes() == palette_result.tobytes()
            else:
                assert new_image.palette is None

        _make_new(im, im_p, ImagePalette.ImagePalette("RGB"))
        _make_new(im_p, im, None)
        _make_new(im, blank_p, ImagePalette.ImagePalette())
        _make_new(im, blank_pa, ImagePalette.ImagePalette())

    @pytest.mark.parametrize(
        "mode, color",
        (
            ("RGB", "#DDEEFF"),
            ("RGB", (221, 238, 255)),
            ("RGBA", (221, 238, 255, 255)),
        ),
    )
    def test_p_from_rgb_rgba(self, mode: str, color: str | tuple[int, ...]) -> None:
        im = Image.new("P", (100, 100), color)
        expected = Image.new(mode, (100, 100), color)
        assert_image_equal(im.convert(mode), expected)

    def test_no_resource_warning_on_save(self, tmp_path: Path) -> None:
        # https://github.com/python-pillow/Pillow/issues/835
        # Arrange
        test_file = "Tests/images/hopper.png"
        temp_file = tmp_path / "temp.jpg"

        # Act/Assert
        with Image.open(test_file) as im:
            with warnings.catch_warnings():
                warnings.simplefilter("error")

                im.save(temp_file)

    def test_no_new_file_on_error(self, tmp_path: Path) -> None:
        temp_file = tmp_path / "temp.jpg"

        im = Image.new("RGB", (0, 0))
        with pytest.raises(ValueError):
            im.save(temp_file)

        assert not os.path.exists(temp_file)

    def test_load_on_nonexclusive_multiframe(self) -> None:
        with open("Tests/images/frozenpond.mpo", "rb") as fp:

            def act(fp: IO[bytes]) -> None:
                im = Image.open(fp)
                im.load()

            act(fp)

            with Image.open(fp) as im:
                im.load()

            assert not fp.closed

    def test_empty_exif(self) -> None:
        with Image.open("Tests/images/exif.png") as im:
            exif = im.getexif()
        assert dict(exif)

        # Test that exif data is cleared after another load
        exif.load(b"")
        assert not dict(exif)

        # Test loading just the EXIF header
        exif.load(b"Exif\x00\x00")
        assert not dict(exif)

    def test_duplicate_exif_header(self) -> None:
        with Image.open("Tests/images/exif.png") as im:
            im.load()
            im.info["exif"] = b"Exif\x00\x00" + im.info["exif"]

            exif = im.getexif()
        assert exif[274] == 1

    def test_empty_get_ifd(self) -> None:
        exif = Image.Exif()
        ifd = exif.get_ifd(0x8769)
        assert ifd == {}

        ifd[36864] = b"0220"
        assert exif.get_ifd(0x8769) == {36864: b"0220"}

        reloaded_exif = Image.Exif()
        reloaded_exif.load(exif.tobytes())
        assert reloaded_exif.get_ifd(0x8769) == {36864: b"0220"}

    @mark_if_feature_version(
        pytest.mark.valgrind_known_error, "libjpeg_turbo", "2.0", reason="Known Failing"
    )
    def test_exif_jpeg(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/exif-72dpi-int.jpg") as im:  # Little endian
            exif = im.getexif()
            assert 258 not in exif
            assert 274 in exif
            assert 282 in exif
            assert exif[296] == 2
            assert exif[11] == "gThumb 3.0.1"

            out = tmp_path / "temp.jpg"
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

            out = tmp_path / "temp.jpg"
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
    def test_exif_webp(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/hopper.webp") as im:
            exif = im.getexif()
            assert exif == {}

            out = tmp_path / "temp.webp"
            exif[258] = 8
            exif[40963] = 455
            exif[305] = "Pillow test"

            def check_exif() -> None:
                with Image.open(out) as reloaded:
                    reloaded_exif = reloaded.getexif()
                    assert reloaded_exif[258] == 8
                    assert reloaded_exif[40963] == 455
                    assert reloaded_exif[305] == "Pillow test"

            im.save(out, exif=exif)
            check_exif()
            im.save(out, exif=exif, save_all=True)
            check_exif()

    def test_exif_png(self, tmp_path: Path) -> None:
        with Image.open("Tests/images/exif.png") as im:
            exif = im.getexif()
            assert exif == {274: 1}

            out = tmp_path / "temp.png"
            exif[258] = 8
            del exif[274]
            exif[40963] = 455
            exif[305] = "Pillow test"
            im.save(out, exif=exif)

        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            assert reloaded_exif == {258: 8, 40963: 455, 305: "Pillow test"}

    def test_exif_interop(self) -> None:
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

    def test_exif_ifd1(self) -> None:
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()
            assert exif.get_ifd(ExifTags.IFD.IFD1) == {
                513: 2036,
                514: 5448,
                259: 6,
                296: 2,
                282: 180.0,
                283: 180.0,
            }

    def test_exif_ifd(self) -> None:
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()
        del exif.get_ifd(0x8769)[0xA005]

        reloaded_exif = Image.Exif()
        reloaded_exif.load(exif.tobytes())
        assert reloaded_exif.get_ifd(0x8769) == exif.get_ifd(0x8769)

    def test_exif_load_from_fp(self) -> None:
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

    def test_exif_hide_offsets(self) -> None:
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()

        # Check offsets are present initially
        assert 0x8769 in exif
        for tag in (0xA005, 0x927C):
            assert tag in exif.get_ifd(0x8769)
        assert exif.get_ifd(0xA005)
        loaded_exif = exif

        with Image.open("Tests/images/flower.jpg") as im:
            new_exif = im.getexif()

            for exif in (loaded_exif, new_exif):
                exif.hide_offsets()

                # Assert they are hidden afterwards,
                # but that the IFDs are still available
                assert 0x8769 not in exif
                assert exif.get_ifd(0x8769)
                for tag in (0xA005, 0x927C):
                    assert tag not in exif.get_ifd(0x8769)
                assert exif.get_ifd(0xA005)

    def test_exif_from_xmp_bytes(self) -> None:
        im = Image.new("RGB", (1, 1))
        im.info["xmp"] = b'\xff tiff:Orientation="2"'
        assert im.getexif()[274] == 2

    def test_empty_xmp(self) -> None:
        with Image.open("Tests/images/hopper.gif") as im:
            if ElementTree is None:
                with pytest.warns(
                    UserWarning,
                    match="XMP data cannot be read without defusedxml dependency",
                ):
                    xmp = im.getxmp()
            else:
                xmp = im.getxmp()
            assert xmp == {}

    def test_getxmp_padded(self) -> None:
        im = Image.new("RGB", (1, 1))
        im.info["xmp"] = (
            b'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
            b'<x:xmpmeta xmlns:x="adobe:ns:meta/" />\n<?xpacket end="w"?>\x00\x00 '
        )
        if ElementTree is None:
            with pytest.warns(
                UserWarning,
                match="XMP data cannot be read without defusedxml dependency",
            ):
                assert im.getxmp() == {}
        else:
            assert im.getxmp() == {"xmpmeta": None}

    def test_get_child_images(self) -> None:
        im = Image.new("RGB", (1, 1))
        with pytest.warns(DeprecationWarning, match="Image.Image.get_child_images"):
            assert im.get_child_images() == []

    @pytest.mark.parametrize("size", ((1, 0), (0, 1), (0, 0)))
    def test_zero_tobytes(self, size: tuple[int, int]) -> None:
        im = Image.new("RGB", size)
        assert im.tobytes() == b""

    @pytest.mark.parametrize("size", ((1, 0), (0, 1), (0, 0)))
    def test_zero_frombytes(self, size: tuple[int, int]) -> None:
        Image.frombytes("RGB", size, b"")

        im = Image.new("RGB", size)
        im.frombytes(b"")

    def test_has_transparency_data(self) -> None:
        for mode in ("1", "L", "P", "RGB"):
            im = Image.new(mode, (1, 1))
            assert not im.has_transparency_data

        for mode in ("LA", "La", "PA", "RGBA", "RGBa"):
            im = Image.new(mode, (1, 1))
            assert im.has_transparency_data

        # P mode with "transparency" info
        with Image.open("Tests/images/first_frame_transparency.gif") as im:
            assert "transparency" in im.info
            assert im.has_transparency_data

        # RGB mode with "transparency" info
        with Image.open("Tests/images/rgb_trns.png") as im:
            assert "transparency" in im.info
            assert im.has_transparency_data

        # P mode with RGBA palette
        im = Image.new("RGBA", (1, 1)).convert("P")
        assert im.mode == "P"
        assert im.palette is not None
        assert im.palette.mode == "RGBA"
        assert im.has_transparency_data

    def test_apply_transparency(self) -> None:
        im = Image.new("P", (1, 1))
        im.putpalette((0, 0, 0, 1, 1, 1))
        assert im.palette is not None
        assert im.palette.colors == {(0, 0, 0): 0, (1, 1, 1): 1}

        # Test that no transformation is applied without transparency
        im.apply_transparency()
        assert im.palette.colors == {(0, 0, 0): 0, (1, 1, 1): 1}

        # Test that a transparency index is applied
        im.info["transparency"] = 0
        im.apply_transparency()
        assert "transparency" not in im.info
        assert im.palette.colors == {(0, 0, 0, 0): 0, (1, 1, 1, 255): 1}

        # Test that existing transparency is kept
        im = Image.new("P", (1, 1))
        im.putpalette((0, 0, 0, 255, 1, 1, 1, 128), "RGBA")
        im.info["transparency"] = 0
        im.apply_transparency()
        assert im.palette is not None
        assert im.palette.colors == {(0, 0, 0, 0): 0, (1, 1, 1, 128): 1}

        # Test that transparency bytes are applied
        with Image.open("Tests/images/pil123p.png") as im:
            assert isinstance(im.info["transparency"], bytes)
            assert im.palette is not None
            assert im.palette.colors[(27, 35, 6)] == 24
            im.apply_transparency()
            assert im.palette is not None
            assert im.palette.colors[(27, 35, 6, 214)] == 24

    def test_constants(self) -> None:
        for enum in (
            Image.Transpose,
            Image.Transform,
            Image.Resampling,
            Image.Dither,
            Image.Palette,
            Image.Quantize,
        ):
            for name in enum.__members__:
                assert getattr(Image, name) == enum[name]

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
    def test_overrun(self, path: str) -> None:
        """For overrun completeness, test as:
        valgrind pytest -qq Tests/test_image.py::TestImage::test_overrun | grep decode.c
        """
        with Image.open(os.path.join("Tests/images", path)) as im:
            with pytest.raises(OSError) as e:
                im.load()
        buffer_overrun = str(e.value) == "buffer overrun when reading image file"
        truncated = "image file is truncated" in str(e.value)

        assert buffer_overrun or truncated

    def test_fli_overrun2(self) -> None:
        with Image.open("Tests/images/fli_overrun2.bin") as im:
            with pytest.raises(OSError, match="buffer overrun when reading image file"):
                im.seek(1)

    def test_exit_fp(self) -> None:
        with Image.new("L", (1, 1)) as im:
            pass
        assert not hasattr(im, "fp")

    def test_close_graceful(self, caplog: pytest.LogCaptureFixture) -> None:
        with Image.open("Tests/images/hopper.jpg") as im:
            copy = im.copy()
            with caplog.at_level(logging.DEBUG):
                im.close()
                copy.close()
            assert len(caplog.records) == 0
            assert im.fp is None

    def test_deprecation(self) -> None:
        with pytest.warns(DeprecationWarning, match="Image.isImageType"):
            assert not Image.isImageType(None)


class TestImageBytes:
    @pytest.mark.parametrize("mode", Image.MODES + ["BGR;15", "BGR;16", "BGR;24"])
    def test_roundtrip_bytes_constructor(self, mode: str) -> None:
        im = hopper(mode)
        source_bytes = im.tobytes()

        if mode.startswith("BGR;"):
            with pytest.warns(DeprecationWarning, match=mode):
                reloaded = Image.frombytes(mode, im.size, source_bytes)
        else:
            reloaded = Image.frombytes(mode, im.size, source_bytes)
        assert reloaded.tobytes() == source_bytes

    @pytest.mark.parametrize("mode", Image.MODES + ["BGR;15", "BGR;16", "BGR;24"])
    def test_roundtrip_bytes_method(self, mode: str) -> None:
        im = hopper(mode)
        source_bytes = im.tobytes()

        reloaded = helper_image_new(mode, im.size)
        reloaded.frombytes(source_bytes)
        assert reloaded.tobytes() == source_bytes

    @pytest.mark.parametrize("mode", Image.MODES + ["BGR;15", "BGR;16", "BGR;24"])
    def test_getdata_putdata(self, mode: str) -> None:
        if is_big_endian() and mode == "BGR;15":
            pytest.xfail("Known failure of BGR;15 on big-endian")
        im = hopper(mode)
        reloaded = helper_image_new(mode, im.size)
        reloaded.putdata(im.getdata())
        assert_image_equal(im, reloaded)


class MockEncoder(ImageFile.PyEncoder):
    pass


class TestRegistry:
    def test_encode_registry(self) -> None:
        Image.register_encoder("MOCK", MockEncoder)
        assert "MOCK" in Image.ENCODERS

        enc = Image._getencoder("RGB", "MOCK", ("args",), extra=("extra",))

        assert isinstance(enc, MockEncoder)
        assert enc.mode == "RGB"
        assert enc.args == ("args", "extra")

    def test_encode_registry_fail(self) -> None:
        with pytest.raises(OSError):
            Image._getencoder("RGB", "DoesNotExist", ("args",), extra=("extra",))
