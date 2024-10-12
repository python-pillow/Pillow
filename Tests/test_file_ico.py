from __future__ import annotations

import io
import os
from pathlib import Path

import pytest

from PIL import IcoImagePlugin, Image, ImageDraw, ImageFile

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

TEST_ICO_FILE = "Tests/images/hopper.ico"


def test_sanity() -> None:
    with Image.open(TEST_ICO_FILE) as im:
        im.load()
    assert im.mode == "RGBA"
    assert im.size == (16, 16)
    assert im.format == "ICO"
    assert im.get_format_mimetype() == "image/x-icon"


def test_load() -> None:
    with Image.open(TEST_ICO_FILE) as im:
        assert im.load()[0, 0] == (1, 1, 9, 255)


def test_mask() -> None:
    with Image.open("Tests/images/hopper_mask.ico") as im:
        assert_image_equal_tofile(im, "Tests/images/hopper_mask.png")


def test_black_and_white() -> None:
    with Image.open("Tests/images/black_and_white.ico") as im:
        assert im.mode == "RGBA"
        assert im.size == (16, 16)


def test_palette(tmp_path: Path) -> None:
    temp_file = str(tmp_path / "temp.ico")

    im = Image.new("P", (16, 16))
    im.save(temp_file)

    with Image.open(temp_file) as reloaded:
        assert reloaded.mode == "P"
        assert reloaded.palette is not None


def test_invalid_file() -> None:
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            IcoImagePlugin.IcoImageFile(fp)


def test_save_to_bytes() -> None:
    output = io.BytesIO()
    im = hopper()
    im.save(output, "ico", sizes=[(32, 32), (64, 64)])

    # The default image
    output.seek(0)
    with Image.open(output) as reloaded:
        assert reloaded.info["sizes"] == {(32, 32), (64, 64)}

        assert im.mode == reloaded.mode
        assert (64, 64) == reloaded.size
        assert reloaded.format == "ICO"
        assert_image_equal(
            reloaded, hopper().resize((64, 64), Image.Resampling.LANCZOS)
        )

    # The other one
    output.seek(0)
    with Image.open(output) as reloaded:
        reloaded.size = (32, 32)

        assert im.mode == reloaded.mode
        assert (32, 32) == reloaded.size
        assert reloaded.format == "ICO"
        assert_image_equal(
            reloaded, hopper().resize((32, 32), Image.Resampling.LANCZOS)
        )


def test_getpixel(tmp_path: Path) -> None:
    temp_file = str(tmp_path / "temp.ico")

    im = hopper()
    im.save(temp_file, "ico", sizes=[(32, 32), (64, 64)])

    with Image.open(temp_file) as reloaded:
        reloaded.load()
        reloaded.size = (32, 32)

        assert reloaded.getpixel((0, 0)) == (18, 20, 62)


def test_no_duplicates(tmp_path: Path) -> None:
    temp_file = str(tmp_path / "temp.ico")
    temp_file2 = str(tmp_path / "temp2.ico")

    im = hopper()
    sizes = [(32, 32), (64, 64)]
    im.save(temp_file, "ico", sizes=sizes)

    sizes.append(sizes[-1])
    im.save(temp_file2, "ico", sizes=sizes)

    assert os.path.getsize(temp_file) == os.path.getsize(temp_file2)


def test_different_bit_depths(tmp_path: Path) -> None:
    temp_file = str(tmp_path / "temp.ico")
    temp_file2 = str(tmp_path / "temp2.ico")

    im = hopper()
    im.save(temp_file, "ico", bitmap_format="bmp", sizes=[(128, 128)])

    hopper("1").save(
        temp_file2,
        "ico",
        bitmap_format="bmp",
        sizes=[(128, 128)],
        append_images=[im],
    )

    assert os.path.getsize(temp_file) != os.path.getsize(temp_file2)

    # Test that only matching sizes of different bit depths are saved
    temp_file3 = str(tmp_path / "temp3.ico")
    temp_file4 = str(tmp_path / "temp4.ico")

    im.save(temp_file3, "ico", bitmap_format="bmp", sizes=[(128, 128)])
    im.save(
        temp_file4,
        "ico",
        bitmap_format="bmp",
        sizes=[(128, 128)],
        append_images=[Image.new("P", (64, 64))],
    )

    assert os.path.getsize(temp_file3) == os.path.getsize(temp_file4)


@pytest.mark.parametrize("mode", ("1", "L", "P", "RGB", "RGBA"))
def test_save_to_bytes_bmp(mode: str) -> None:
    output = io.BytesIO()
    im = hopper(mode)
    im.save(output, "ico", bitmap_format="bmp", sizes=[(32, 32), (64, 64)])

    # The default image
    output.seek(0)
    with Image.open(output) as reloaded:
        assert reloaded.info["sizes"] == {(32, 32), (64, 64)}

        assert "RGBA" == reloaded.mode
        assert (64, 64) == reloaded.size
        assert reloaded.format == "ICO"
        im = hopper(mode).resize((64, 64), Image.Resampling.LANCZOS).convert("RGBA")
        assert_image_equal(reloaded, im)

    # The other one
    output.seek(0)
    with Image.open(output) as reloaded:
        reloaded.size = (32, 32)

        assert "RGBA" == reloaded.mode
        assert (32, 32) == reloaded.size
        assert reloaded.format == "ICO"
        im = hopper(mode).resize((32, 32), Image.Resampling.LANCZOS).convert("RGBA")
        assert_image_equal(reloaded, im)


def test_incorrect_size() -> None:
    with Image.open(TEST_ICO_FILE) as im:
        with pytest.raises(ValueError):
            im.size = (1, 1)


def test_save_256x256(tmp_path: Path) -> None:
    """Issue #2264 https://github.com/python-pillow/Pillow/issues/2264"""
    # Arrange
    with Image.open("Tests/images/hopper_256x256.ico") as im:
        outfile = str(tmp_path / "temp_saved_hopper_256x256.ico")

        # Act
        im.save(outfile)
    with Image.open(outfile) as im_saved:
        # Assert
        assert im_saved.size == (256, 256)


def test_only_save_relevant_sizes(tmp_path: Path) -> None:
    """Issue #2266 https://github.com/python-pillow/Pillow/issues/2266
    Should save in 16x16, 24x24, 32x32, 48x48 sizes
    and not in 16x16, 24x24, 32x32, 48x48, 48x48, 48x48, 48x48 sizes
    """
    # Arrange
    with Image.open("Tests/images/python.ico") as im:  # 16x16, 32x32, 48x48
        outfile = str(tmp_path / "temp_saved_python.ico")
        # Act
        im.save(outfile)

    with Image.open(outfile) as im_saved:
        # Assert
        assert im_saved.info["sizes"] == {(16, 16), (24, 24), (32, 32), (48, 48)}


def test_save_append_images(tmp_path: Path) -> None:
    # append_images should be used for scaled down versions of the image
    im = hopper("RGBA")
    provided_im = Image.new("RGBA", (32, 32), (255, 0, 0))
    outfile = str(tmp_path / "temp_saved_multi_icon.ico")
    im.save(outfile, sizes=[(32, 32), (128, 128)], append_images=[provided_im])

    with Image.open(outfile) as reread:
        assert_image_equal(reread, hopper("RGBA"))

        reread.size = (32, 32)
        assert_image_equal(reread, provided_im)


def test_unexpected_size() -> None:
    # This image has been manually hexedited to state that it is 16x32
    # while the image within is still 16x16
    with pytest.warns(UserWarning):
        with Image.open("Tests/images/hopper_unexpected.ico") as im:
            assert im.size == (16, 16)


def test_draw_reloaded(tmp_path: Path) -> None:
    with Image.open(TEST_ICO_FILE) as im:
        outfile = str(tmp_path / "temp_saved_hopper_draw.ico")

        draw = ImageDraw.Draw(im)
        draw.line((0, 0) + im.size, "#f00")
        im.save(outfile)

    with Image.open(outfile) as im:
        assert_image_equal_tofile(im, "Tests/images/hopper_draw.ico")


def test_truncated_mask() -> None:
    # 1 bpp
    with open("Tests/images/hopper_mask.ico", "rb") as fp:
        data = fp.read()

    ImageFile.LOAD_TRUNCATED_IMAGES = True
    data = data[:-3]

    try:
        with Image.open(io.BytesIO(data)) as im:
            with Image.open("Tests/images/hopper_mask.png") as expected:
                assert im.mode == "1"

        # 32 bpp
        output = io.BytesIO()
        expected = hopper("RGBA")
        expected.save(output, "ico", bitmap_format="bmp")

        data = output.getvalue()[:-1]

        with Image.open(io.BytesIO(data)) as im:
            assert im.mode == "RGB"
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False
