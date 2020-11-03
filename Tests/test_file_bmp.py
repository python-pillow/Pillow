import io

import pytest

from PIL import BmpImagePlugin, Image

from .helper import assert_image_equal, hopper


def test_sanity(tmp_path):
    def roundtrip(im):
        outfile = str(tmp_path / "temp.bmp")

        im.save(outfile, "BMP")

        with Image.open(outfile) as reloaded:
            reloaded.load()
            assert im.mode == reloaded.mode
            assert im.size == reloaded.size
            assert reloaded.format == "BMP"
            assert reloaded.get_format_mimetype() == "image/bmp"

    roundtrip(hopper())

    roundtrip(hopper("1"))
    roundtrip(hopper("L"))
    roundtrip(hopper("P"))
    roundtrip(hopper("RGB"))


def test_invalid_file():
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            BmpImagePlugin.BmpImageFile(fp)


def test_save_to_bytes():
    output = io.BytesIO()
    im = hopper()
    im.save(output, "BMP")

    output.seek(0)
    with Image.open(output) as reloaded:
        assert im.mode == reloaded.mode
        assert im.size == reloaded.size
        assert reloaded.format == "BMP"


def test_save_too_large(tmp_path):
    outfile = str(tmp_path / "temp.bmp")
    with Image.new("RGB", (1, 1)) as im:
        im._size = (37838, 37838)
        with pytest.raises(ValueError):
            im.save(outfile)


def test_dpi():
    dpi = (72, 72)

    output = io.BytesIO()
    with hopper() as im:
        im.save(output, "BMP", dpi=dpi)

    output.seek(0)
    with Image.open(output) as reloaded:
        assert reloaded.info["dpi"] == dpi


def test_save_bmp_with_dpi(tmp_path):
    # Test for #1301
    # Arrange
    outfile = str(tmp_path / "temp.jpg")
    with Image.open("Tests/images/hopper.bmp") as im:

        # Act
        im.save(outfile, "JPEG", dpi=im.info["dpi"])

        # Assert
        with Image.open(outfile) as reloaded:
            reloaded.load()
            assert im.info["dpi"] == reloaded.info["dpi"]
            assert im.size == reloaded.size
            assert reloaded.format == "JPEG"


def test_load_dpi_rounding():
    # Round up
    with Image.open("Tests/images/hopper.bmp") as im:
        assert im.info["dpi"] == (96, 96)

    # Round down
    with Image.open("Tests/images/hopper_roundDown.bmp") as im:
        assert im.info["dpi"] == (72, 72)


def test_save_dpi_rounding(tmp_path):
    outfile = str(tmp_path / "temp.bmp")
    with Image.open("Tests/images/hopper.bmp") as im:
        im.save(outfile, dpi=(72.2, 72.2))
        with Image.open(outfile) as reloaded:
            assert reloaded.info["dpi"] == (72, 72)

        im.save(outfile, dpi=(72.8, 72.8))
    with Image.open(outfile) as reloaded:
        assert reloaded.info["dpi"] == (73, 73)


def test_load_dib():
    # test for #1293, Imagegrab returning Unsupported Bitfields Format
    with Image.open("Tests/images/clipboard.dib") as im:
        assert im.format == "DIB"
        assert im.get_format_mimetype() == "image/bmp"

        with Image.open("Tests/images/clipboard_target.png") as target:
            assert_image_equal(im, target)


def test_save_dib(tmp_path):
    outfile = str(tmp_path / "temp.dib")

    with Image.open("Tests/images/clipboard.dib") as im:
        im.save(outfile)

        with Image.open(outfile) as reloaded:
            assert reloaded.format == "DIB"
            assert reloaded.get_format_mimetype() == "image/bmp"
            assert_image_equal(im, reloaded)


def test_rgba_bitfields():
    # This test image has been manually hexedited
    # to change the bitfield compression in the header from XBGR to RGBA
    with Image.open("Tests/images/rgb32bf-rgba.bmp") as im:

        # So before the comparing the image, swap the channels
        b, g, r = im.split()[1:]
        im = Image.merge("RGB", (r, g, b))

    with Image.open("Tests/images/bmp/q/rgb32bf-xbgr.bmp") as target:
        assert_image_equal(im, target)
