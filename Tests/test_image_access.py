from __future__ import annotations

import os
import subprocess
import sys
import sysconfig
from types import ModuleType

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper, is_win32

numpy: ModuleType | None
try:
    import numpy
except ImportError:
    numpy = None


class TestImagePutPixel:
    def test_sanity(self) -> None:
        im1 = hopper()
        im2 = Image.new(im1.mode, im1.size, 0)

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pos = x, y
                value = im1.getpixel(pos)
                assert value is not None
                im2.putpixel(pos, value)

        assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)
        im2.readonly = 1

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pos = x, y
                value = im1.getpixel(pos)
                assert value is not None
                im2.putpixel(pos, value)

        assert not im2.readonly
        assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)

        pix1 = im1.load()
        pix2 = im2.load()

        assert pix1 is not None
        assert pix2 is not None
        with pytest.raises(TypeError):
            pix1[0, "0"]  # type: ignore[index]
        with pytest.raises(TypeError):
            pix1["0", 0]  # type: ignore[index]

        for y in range(im1.size[1]):
            for x in range(im1.size[0]):
                pix2[x, y] = pix1[x, y]

        assert_image_equal(im1, im2)

    def test_sanity_negative_index(self) -> None:
        im1 = hopper()
        im2 = Image.new(im1.mode, im1.size, 0)

        width, height = im1.size
        assert im1.getpixel((0, 0)) == im1.getpixel((-width, -height))
        assert im1.getpixel((-1, -1)) == im1.getpixel((width - 1, height - 1))

        for y in range(-1, -im1.size[1] - 1, -1):
            for x in range(-1, -im1.size[0] - 1, -1):
                pos = x, y
                value = im1.getpixel(pos)
                assert value is not None
                im2.putpixel(pos, value)

        assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)
        im2.readonly = 1

        for y in range(-1, -im1.size[1] - 1, -1):
            for x in range(-1, -im1.size[0] - 1, -1):
                pos = x, y
                value = im1.getpixel(pos)
                assert value is not None
                im2.putpixel(pos, value)

        assert not im2.readonly
        assert_image_equal(im1, im2)

        im2 = Image.new(im1.mode, im1.size, 0)

        pix1 = im1.load()
        pix2 = im2.load()

        assert pix1 is not None
        assert pix2 is not None
        for y in range(-1, -im1.size[1] - 1, -1):
            for x in range(-1, -im1.size[0] - 1, -1):
                pix2[x, y] = pix1[x, y]

        assert_image_equal(im1, im2)

    @pytest.mark.skipif(numpy is None, reason="NumPy not installed")
    def test_numpy(self) -> None:
        im = hopper()
        px = im.load()

        assert px is not None
        assert numpy is not None
        assert px[numpy.int32(1), numpy.int32(2)] == (18, 20, 59)


class TestImageGetPixel:
    @staticmethod
    def color(mode: str) -> int | tuple[int, ...]:
        bands = Image.getmodebands(mode)
        if bands == 1:
            return 1
        if mode in ("BGR;15", "BGR;16"):
            # These modes have less than 8 bits per band,
            # so (1, 2, 3) cannot be roundtripped.
            return (16, 32, 49)
        return tuple(range(1, bands + 1))

    def check(self, mode: str, expected_color_int: int | None = None) -> None:
        expected_color = (
            self.color(mode) if expected_color_int is None else expected_color_int
        )

        # Check putpixel
        im = Image.new(mode, (1, 1), None)
        im.putpixel((0, 0), expected_color)
        actual_color = im.getpixel((0, 0))
        assert actual_color == expected_color, (
            f"put/getpixel roundtrip failed for mode {mode}, "
            f"expected {expected_color} got {actual_color}"
        )

        # Check putpixel negative index
        im.putpixel((-1, -1), expected_color)
        actual_color = im.getpixel((-1, -1))
        assert actual_color == expected_color, (
            f"put/getpixel roundtrip negative index failed for mode {mode}, "
            f"expected {expected_color} got {actual_color}"
        )

        # Check 0x0 image with None initial color
        im = Image.new(mode, (0, 0), None)
        assert im.load() is not None
        with pytest.raises(IndexError):
            im.putpixel((0, 0), expected_color)
        with pytest.raises(IndexError):
            im.getpixel((0, 0))
        # Check negative index
        with pytest.raises(IndexError):
            im.putpixel((-1, -1), expected_color)
        with pytest.raises(IndexError):
            im.getpixel((-1, -1))

        # Check initial color
        im = Image.new(mode, (1, 1), expected_color)
        actual_color = im.getpixel((0, 0))
        assert actual_color == expected_color, (
            f"initial color failed for mode {mode}, "
            f"expected {expected_color} got {actual_color}"
        )

        # Check initial color negative index
        actual_color = im.getpixel((-1, -1))
        assert actual_color == expected_color, (
            f"initial color failed with negative index for mode {mode}, "
            f"expected {expected_color} got {actual_color}"
        )

        # Check 0x0 image with initial color
        im = Image.new(mode, (0, 0), expected_color)
        with pytest.raises(IndexError):
            im.getpixel((0, 0))
        # Check negative index
        with pytest.raises(IndexError):
            im.getpixel((-1, -1))

    @pytest.mark.parametrize("mode", Image.MODES)
    def test_basic(self, mode: str) -> None:
        self.check(mode)

    @pytest.mark.parametrize("mode", ("BGR;15", "BGR;16", "BGR;24"))
    def test_deprecated(self, mode: str) -> None:
        with pytest.warns(DeprecationWarning):
            self.check(mode)

    def test_list(self) -> None:
        im = hopper()
        assert im.getpixel([0, 0]) == (20, 20, 70)

    @pytest.mark.parametrize("mode", ("I;16", "I;16B"))
    @pytest.mark.parametrize("expected_color", (2**15 - 1, 2**15, 2**15 + 1, 2**16 - 1))
    def test_signedness(self, mode: str, expected_color: int) -> None:
        # See https://github.com/python-pillow/Pillow/issues/452
        # pixelaccess is using signed int* instead of uint*
        self.check(mode, expected_color)

    @pytest.mark.parametrize("mode", ("P", "PA"))
    @pytest.mark.parametrize("color", ((255, 0, 0), (255, 0, 0, 255)))
    def test_p_putpixel_rgb_rgba(self, mode: str, color: tuple[int, ...]) -> None:
        im = Image.new(mode, (1, 1))
        im.putpixel((0, 0), color)

        alpha = color[3] if len(color) == 4 and mode == "PA" else 255
        assert im.convert("RGBA").getpixel((0, 0)) == (255, 0, 0, alpha)


class TestImagePutPixelError:
    IMAGE_MODES1 = ["LA", "RGB", "RGBA", "BGR;15"]
    IMAGE_MODES2 = ["L", "I", "I;16"]
    INVALID_TYPES = ["foo", 1.0, None]

    @pytest.mark.parametrize("mode", IMAGE_MODES1)
    def test_putpixel_type_error1(self, mode: str) -> None:
        im = hopper(mode)
        for v in self.INVALID_TYPES:
            with pytest.raises(TypeError, match="color must be int or tuple"):
                im.putpixel((0, 0), v)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "mode, band_numbers, match",
        (
            ("L", (0, 2), "color must be int or single-element tuple"),
            ("LA", (0, 3), "color must be int, or tuple of one or two elements"),
            (
                "BGR;15",
                (0, 2),
                "color must be int, or tuple of one or three elements",
            ),
            (
                "RGB",
                (0, 2, 5),
                "color must be int, or tuple of one, three or four elements",
            ),
        ),
    )
    def test_putpixel_invalid_number_of_bands(
        self, mode: str, band_numbers: tuple[int, ...], match: str
    ) -> None:
        im = hopper(mode)
        for band_number in band_numbers:
            with pytest.raises(TypeError, match=match):
                im.putpixel((0, 0), (0,) * band_number)

    @pytest.mark.parametrize("mode", IMAGE_MODES2)
    def test_putpixel_type_error2(self, mode: str) -> None:
        im = hopper(mode)
        for v in self.INVALID_TYPES:
            with pytest.raises(
                TypeError, match="color must be int or single-element tuple"
            ):
                im.putpixel((0, 0), v)  # type: ignore[arg-type]

    @pytest.mark.parametrize("mode", IMAGE_MODES1 + IMAGE_MODES2)
    def test_putpixel_overflow_error(self, mode: str) -> None:
        im = hopper(mode)
        with pytest.raises(OverflowError):
            im.putpixel((0, 0), 2**80)


class TestEmbeddable:
    @pytest.mark.xfail(reason="failing test")
    @pytest.mark.skipif(not is_win32(), reason="requires Windows")
    def test_embeddable(self) -> None:
        import ctypes

        from setuptools.command import build_ext

        with open("embed_pil.c", "w", encoding="utf-8") as fh:
            home = sys.prefix.replace("\\", "\\\\")
            fh.write(
                f"""
#include "Python.h"

int main(int argc, char* argv[])
{{
    char *home = "{home}";
    wchar_t *whome = Py_DecodeLocale(home, NULL);
    Py_SetPythonHome(whome);

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

    Py_InitializeEx(0);
    Py_DECREF(PyImport_ImportModule("PIL.Image"));
    Py_Finalize();

    PyMem_RawFree(whome);

    return 0;
}}
        """
            )

        compiler = getattr(build_ext, "new_compiler")()
        compiler.add_include_dir(sysconfig.get_config_var("INCLUDEPY"))

        libdir = sysconfig.get_config_var("LIBDIR") or sysconfig.get_config_var(
            "INCLUDEPY"
        ).replace("include", "libs")
        compiler.add_library_dir(libdir)
        objects = compiler.compile(["embed_pil.c"])
        compiler.link_executable(objects, "embed_pil")

        env = os.environ.copy()
        env["PATH"] = sys.prefix + ";" + env["PATH"]

        # Do not display the Windows Error Reporting dialog
        getattr(ctypes, "windll").kernel32.SetErrorMode(0x0002)

        process = subprocess.Popen(["embed_pil.exe"], env=env)
        process.communicate()
        assert process.returncode == 0
