"""Test DdsImagePlugin"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from PIL import DdsImagePlugin, Image

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
)

TEST_FILE_DXT1 = "Tests/images/dxt1-rgb-4bbp-noalpha_MipMaps-1.dds"
TEST_FILE_DXT3 = "Tests/images/dxt3-argb-8bbp-explicitalpha_MipMaps-1.dds"
TEST_FILE_DXT5 = "Tests/images/dxt5-argb-8bbp-interpolatedalpha_MipMaps-1.dds"
TEST_FILE_ATI1 = "Tests/images/ati1.dds"
TEST_FILE_ATI2 = "Tests/images/ati2.dds"
TEST_FILE_DX10_BC4_TYPELESS = "Tests/images/bc4_typeless.dds"
TEST_FILE_DX10_BC4_UNORM = "Tests/images/bc4_unorm.dds"
TEST_FILE_DX10_BC5_TYPELESS = "Tests/images/bc5_typeless.dds"
TEST_FILE_DX10_BC5_UNORM = "Tests/images/bc5_unorm.dds"
TEST_FILE_DX10_BC5_SNORM = "Tests/images/bc5_snorm.dds"
TEST_FILE_DX10_BC1 = "Tests/images/bc1.dds"
TEST_FILE_DX10_BC1_TYPELESS = "Tests/images/bc1_typeless.dds"
TEST_FILE_BC4U = "Tests/images/bc4u.dds"
TEST_FILE_BC5S = "Tests/images/bc5s.dds"
TEST_FILE_BC5U = "Tests/images/bc5u.dds"
TEST_FILE_BC6H = "Tests/images/bc6h.dds"
TEST_FILE_BC6HS = "Tests/images/bc6h_sf.dds"
TEST_FILE_DX10_BC7 = "Tests/images/bc7-argb-8bpp_MipMaps-1.dds"
TEST_FILE_DX10_BC7_UNORM_SRGB = "Tests/images/DXGI_FORMAT_BC7_UNORM_SRGB.dds"
TEST_FILE_DX10_R8G8B8A8 = "Tests/images/argb-32bpp_MipMaps-1.dds"
TEST_FILE_DX10_R8G8B8A8_UNORM_SRGB = "Tests/images/DXGI_FORMAT_R8G8B8A8_UNORM_SRGB.dds"
TEST_FILE_UNCOMPRESSED_L = "Tests/images/uncompressed_l.dds"
TEST_FILE_UNCOMPRESSED_L_WITH_ALPHA = "Tests/images/uncompressed_la.dds"
TEST_FILE_UNCOMPRESSED_RGB = "Tests/images/hopper.dds"
TEST_FILE_UNCOMPRESSED_BGR15 = "Tests/images/bgr15.dds"
TEST_FILE_UNCOMPRESSED_RGB_WITH_ALPHA = "Tests/images/uncompressed_rgb.dds"


@pytest.mark.parametrize(
    "image_path",
    (
        TEST_FILE_DXT1,
        # hexeditted to use DX10 FourCC
        TEST_FILE_DX10_BC1,
        TEST_FILE_DX10_BC1_TYPELESS,
    ),
)
def test_sanity_dxt1_bc1(image_path: str) -> None:
    """Check DXT1 and BC1 images can be opened"""
    with Image.open(TEST_FILE_DXT1.replace(".dds", ".png")) as target:
        target = target.convert("RGBA")
    with Image.open(image_path) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGBA"
        assert im.size == (256, 256)

        assert_image_equal(im, target)


def test_sanity_dxt3() -> None:
    """Check DXT3 images can be opened"""

    with Image.open(TEST_FILE_DXT3) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGBA"
        assert im.size == (256, 256)

        assert_image_equal_tofile(im, TEST_FILE_DXT3.replace(".dds", ".png"))


def test_sanity_dxt5() -> None:
    """Check DXT5 images can be opened"""

    with Image.open(TEST_FILE_DXT5) as im:
        im.load()

    assert im.format == "DDS"
    assert im.mode == "RGBA"
    assert im.size == (256, 256)

    assert_image_equal_tofile(im, TEST_FILE_DXT5.replace(".dds", ".png"))


@pytest.mark.parametrize(
    "image_path",
    (
        TEST_FILE_ATI1,
        # hexeditted to use BC4U FourCC
        TEST_FILE_BC4U,
    ),
)
def test_sanity_ati1_bc4u(image_path: str) -> None:
    """Check ATI1 and BC4U images can be opened"""

    with Image.open(image_path) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "L"
        assert im.size == (64, 64)

        assert_image_equal_tofile(im, TEST_FILE_ATI1.replace(".dds", ".png"))


def test_dx10_bc2(tmp_path: Path) -> None:
    out = tmp_path / "temp.dds"
    with Image.open(TEST_FILE_DXT3) as im:
        im.save(out, pixel_format="BC2")

    with Image.open(out) as reloaded:
        assert reloaded.format == "DDS"
        assert reloaded.mode == "RGBA"
        assert reloaded.size == (256, 256)

        assert_image_similar(im, reloaded, 3.81)


def test_dx10_bc3(tmp_path: Path) -> None:
    out = tmp_path / "temp.dds"
    with Image.open(TEST_FILE_DXT5) as im:
        im.save(out, pixel_format="BC3")

    with Image.open(out) as reloaded:
        assert reloaded.format == "DDS"
        assert reloaded.mode == "RGBA"
        assert reloaded.size == (256, 256)

        assert_image_similar(im, reloaded, 3.69)


@pytest.mark.parametrize(
    "image_path",
    (
        TEST_FILE_DX10_BC4_UNORM,
        # hexeditted to be typeless
        TEST_FILE_DX10_BC4_TYPELESS,
    ),
)
def test_dx10_bc4(image_path: str) -> None:
    """Check DX10 BC4 images can be opened"""

    with Image.open(image_path) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "L"
        assert im.size == (64, 64)

        assert_image_equal_tofile(im, TEST_FILE_DX10_BC4_UNORM.replace(".dds", ".png"))


@pytest.mark.parametrize(
    "image_path",
    (
        TEST_FILE_ATI2,
        # hexeditted to use BC5U FourCC
        TEST_FILE_BC5U,
    ),
)
def test_sanity_ati2_bc5u(image_path: str) -> None:
    """Check ATI2 and BC5U images can be opened"""

    with Image.open(image_path) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGB"
        assert im.size == (256, 256)

        assert_image_equal_tofile(im, TEST_FILE_DX10_BC5_UNORM.replace(".dds", ".png"))


@pytest.mark.parametrize(
    "image_path, expected_path",
    (
        # hexeditted to be typeless
        (TEST_FILE_DX10_BC5_TYPELESS, TEST_FILE_DX10_BC5_UNORM),
        (TEST_FILE_DX10_BC5_UNORM, TEST_FILE_DX10_BC5_UNORM),
        # hexeditted to use DX10 FourCC
        (TEST_FILE_DX10_BC5_SNORM, TEST_FILE_BC5S),
        (TEST_FILE_BC5S, TEST_FILE_BC5S),
    ),
)
def test_dx10_bc5(image_path: str, expected_path: str) -> None:
    """Check DX10 BC5 images can be opened"""

    with Image.open(image_path) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGB"
        assert im.size == (256, 256)

        assert_image_equal_tofile(im, expected_path.replace(".dds", ".png"))


@pytest.mark.parametrize("image_path", (TEST_FILE_BC6H, TEST_FILE_BC6HS))
def test_dx10_bc6h(image_path: str) -> None:
    """Check DX10 BC6H/BC6HS images can be opened"""

    with Image.open(image_path) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGB"
        assert im.size == (128, 128)

        assert_image_equal_tofile(im, image_path.replace(".dds", ".png"))


def test_dx10_bc7() -> None:
    """Check DX10 images can be opened"""

    with Image.open(TEST_FILE_DX10_BC7) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGBA"
        assert im.size == (256, 256)

        assert_image_equal_tofile(im, TEST_FILE_DX10_BC7.replace(".dds", ".png"))


def test_dx10_bc7_unorm_srgb() -> None:
    """Check DX10 unsigned normalized integer images can be opened"""

    with Image.open(TEST_FILE_DX10_BC7_UNORM_SRGB) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGBA"
        assert im.size == (16, 16)
        assert im.info["gamma"] == 1 / 2.2

        assert_image_equal_tofile(
            im, TEST_FILE_DX10_BC7_UNORM_SRGB.replace(".dds", ".png")
        )


def test_dx10_r8g8b8a8() -> None:
    """Check DX10 images can be opened"""

    with Image.open(TEST_FILE_DX10_R8G8B8A8) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGBA"
        assert im.size == (256, 256)

        assert_image_equal_tofile(im, TEST_FILE_DX10_R8G8B8A8.replace(".dds", ".png"))


def test_dx10_r8g8b8a8_unorm_srgb() -> None:
    """Check DX10 unsigned normalized integer images can be opened"""

    with Image.open(TEST_FILE_DX10_R8G8B8A8_UNORM_SRGB) as im:
        im.load()

        assert im.format == "DDS"
        assert im.mode == "RGBA"
        assert im.size == (16, 16)
        assert im.info["gamma"] == 1 / 2.2

        assert_image_equal_tofile(
            im, TEST_FILE_DX10_R8G8B8A8_UNORM_SRGB.replace(".dds", ".png")
        )


@pytest.mark.parametrize(
    "mode, size, test_file",
    [
        ("L", (128, 128), TEST_FILE_UNCOMPRESSED_L),
        ("LA", (128, 128), TEST_FILE_UNCOMPRESSED_L_WITH_ALPHA),
        ("RGB", (128, 128), TEST_FILE_UNCOMPRESSED_RGB),
        ("RGB", (128, 128), TEST_FILE_UNCOMPRESSED_BGR15),
        ("RGBA", (800, 600), TEST_FILE_UNCOMPRESSED_RGB_WITH_ALPHA),
    ],
)
def test_uncompressed(mode: str, size: tuple[int, int], test_file: str) -> None:
    """Check uncompressed images can be opened"""

    with Image.open(test_file) as im:
        assert im.format == "DDS"
        assert im.mode == mode
        assert im.size == size

        assert_image_equal_tofile(im, test_file.replace(".dds", ".png"))


def test__accept_true() -> None:
    """Check valid prefix"""
    # Arrange
    prefix = b"DDS etc"

    # Act
    output = DdsImagePlugin._accept(prefix)

    # Assert
    assert output


def test__accept_false() -> None:
    """Check invalid prefix"""
    # Arrange
    prefix = b"something invalid"

    # Act
    output = DdsImagePlugin._accept(prefix)

    # Assert
    assert not output


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        DdsImagePlugin.DdsImageFile(invalid_file)


def test_short_header() -> None:
    """Check a short header"""
    with open(TEST_FILE_DXT5, "rb") as f:
        img_file = f.read()

    def short_header() -> None:
        with Image.open(BytesIO(img_file[:119])):
            pass  # pragma: no cover

    with pytest.raises(OSError):
        short_header()


def test_short_file() -> None:
    """Check that the appropriate error is thrown for a short file"""

    with open(TEST_FILE_DXT5, "rb") as f:
        img_file = f.read()

    def short_file() -> None:
        with Image.open(BytesIO(img_file[:-100])) as im:
            im.load()

    with pytest.raises(OSError):
        short_file()


def test_dxt5_colorblock_alpha_issue_4142() -> None:
    """Check that colorblocks are decoded correctly in DXT5"""

    with Image.open("Tests/images/dxt5-colorblock-alpha-issue-4142.dds") as im:
        px = im.getpixel((0, 0))
        assert isinstance(px, tuple)
        assert px[0] != 0
        assert px[1] != 0
        assert px[2] != 0

        px = im.getpixel((1, 0))
        assert isinstance(px, tuple)
        assert px[0] != 0
        assert px[1] != 0
        assert px[2] != 0


def test_palette() -> None:
    with Image.open("Tests/images/palette.dds") as im:
        assert_image_equal_tofile(im, "Tests/images/transparent.gif")


def test_unsupported_bitcount() -> None:
    with pytest.raises(OSError):
        with Image.open("Tests/images/unsupported_bitcount.dds"):
            pass


@pytest.mark.parametrize(
    "test_file",
    (
        "Tests/images/unimplemented_dxgi_format.dds",
        "Tests/images/unimplemented_pfflags.dds",
    ),
)
def test_not_implemented(test_file: str) -> None:
    with pytest.raises(NotImplementedError):
        with Image.open(test_file):
            pass


def test_save_unsupported_mode(tmp_path: Path) -> None:
    out = tmp_path / "temp.dds"
    im = hopper("HSV")
    with pytest.raises(OSError, match="cannot write mode HSV as DDS"):
        im.save(out)


@pytest.mark.parametrize(
    "mode, test_file",
    [
        ("L", "Tests/images/linear_gradient.png"),
        ("LA", "Tests/images/uncompressed_la.png"),
        ("RGB", "Tests/images/hopper.png"),
        ("RGBA", "Tests/images/pil123rgba.png"),
    ],
)
def test_save(mode: str, test_file: str, tmp_path: Path) -> None:
    out = tmp_path / "temp.dds"
    with Image.open(test_file) as im:
        assert im.mode == mode
        im.save(out)

        assert_image_equal_tofile(im, out)


def test_save_unsupported_pixel_format(tmp_path: Path) -> None:
    out = tmp_path / "temp.dds"
    im = hopper()
    with pytest.raises(OSError, match="cannot write pixel format UNKNOWN"):
        im.save(out, pixel_format="UNKNOWN")


def test_save_dxt1(tmp_path: Path) -> None:
    # RGB
    out = tmp_path / "temp.dds"
    with Image.open(TEST_FILE_DXT1) as im:
        im.convert("RGB").save(out, pixel_format="DXT1")
    assert_image_similar_tofile(im, out, 1.84)

    # RGBA
    im_alpha = im.copy()
    im_alpha.putpixel((0, 0), (0, 0, 0, 0))
    im_alpha.save(out, pixel_format="DXT1")
    with Image.open(out) as reloaded:
        assert reloaded.getpixel((0, 0)) == (0, 0, 0, 0)

    # L
    im_l = im.convert("L")
    im_l.save(out, pixel_format="DXT1")
    assert_image_similar_tofile(im_l.convert("RGBA"), out, 6.07)

    # LA
    im_alpha.convert("LA").save(out, pixel_format="DXT1")
    with Image.open(out) as reloaded:
        assert reloaded.getpixel((0, 0)) == (0, 0, 0, 0)


def test_save_dxt3(tmp_path: Path) -> None:
    # RGB
    out = tmp_path / "temp.dds"
    with Image.open(TEST_FILE_DXT3) as im:
        im_rgb = im.convert("RGB")
    im_rgb.save(out, pixel_format="DXT3")
    assert_image_similar_tofile(im_rgb.convert("RGBA"), out, 1.26)

    # RGBA
    im.save(out, pixel_format="DXT3")
    assert_image_similar_tofile(im, out, 3.81)

    # L
    im_l = im.convert("L")
    im_l.save(out, pixel_format="DXT3")
    assert_image_similar_tofile(im_l.convert("RGBA"), out, 5.89)

    # LA
    im_la = im.convert("LA")
    im_la.save(out, pixel_format="DXT3")
    assert_image_similar_tofile(im_la.convert("RGBA"), out, 8.44)


def test_save_dxt5(tmp_path: Path) -> None:
    # RGB
    out = tmp_path / "temp.dds"
    with Image.open(TEST_FILE_DXT1) as im:
        im.convert("RGB").save(out, pixel_format="DXT5")
    assert_image_similar_tofile(im, out, 1.84)

    # RGBA
    with Image.open(TEST_FILE_DXT5) as im_rgba:
        im_rgba.save(out, pixel_format="DXT5")
    assert_image_similar_tofile(im_rgba, out, 3.69)

    # L
    im_l = im.convert("L")
    im_l.save(out, pixel_format="DXT5")
    assert_image_similar_tofile(im_l.convert("RGBA"), out, 6.07)

    # LA
    im_la = im_rgba.convert("LA")
    im_la.save(out, pixel_format="DXT5")
    assert_image_similar_tofile(im_la.convert("RGBA"), out, 8.32)


def test_save_dx10_bc5(tmp_path: Path) -> None:
    out = tmp_path / "temp.dds"
    with Image.open(TEST_FILE_DX10_BC5_TYPELESS) as im:
        im.save(out, pixel_format="BC5")
    assert_image_similar_tofile(im, out, 9.56)

    im = hopper("L")
    with pytest.raises(OSError, match="only RGB mode can be written as BC5"):
        im.save(out, pixel_format="BC5")


@pytest.mark.parametrize(
    "pixel_format, mode",
    (
        ("DXT1", "RGBA"),
        ("DXT3", "RGBA"),
        ("DXT5", "RGBA"),
        ("BC2", "RGBA"),
        ("BC3", "RGBA"),
        ("BC5", "RGB"),
    ),
)
def test_save_large_file(tmp_path: Path, pixel_format: str, mode: str) -> None:
    im = hopper(mode).resize((440, 440))
    # should not error in valgrind
    im.save(tmp_path / "img.dds", pixel_format=pixel_format)
