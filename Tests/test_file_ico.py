import io

import pytest

from PIL import IcoImagePlugin, Image, ImageDraw

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

TEST_ICO_FILE = "Tests/images/hopper.ico"


def test_sanity():
    with Image.open(TEST_ICO_FILE) as im:
        im.load()
    assert im.mode == "RGBA"
    assert im.size == (16, 16)
    assert im.format == "ICO"
    assert im.get_format_mimetype() == "image/x-icon"


def test_mask():
    with Image.open("Tests/images/hopper_mask.ico") as im:
        assert_image_equal_tofile(im, "Tests/images/hopper_mask.png")


def test_black_and_white():
    with Image.open("Tests/images/black_and_white.ico") as im:
        assert im.mode == "RGBA"
        assert im.size == (16, 16)


def test_invalid_file():
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            IcoImagePlugin.IcoImageFile(fp)


def test_save_to_bytes():
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
        assert_image_equal(reloaded, hopper().resize((64, 64), Image.LANCZOS))

    # The other one
    output.seek(0)
    with Image.open(output) as reloaded:
        reloaded.size = (32, 32)

        assert im.mode == reloaded.mode
        assert (32, 32) == reloaded.size
        assert reloaded.format == "ICO"
        assert_image_equal(reloaded, hopper().resize((32, 32), Image.LANCZOS))


@pytest.mark.parametrize("mode", ("1", "L", "P", "RGB", "RGBA"))
def test_save_to_bytes_bmp(mode):
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
        im = hopper(mode).resize((64, 64), Image.LANCZOS).convert("RGBA")
        assert_image_equal(reloaded, im)

    # The other one
    output.seek(0)
    with Image.open(output) as reloaded:
        reloaded.size = (32, 32)

        assert "RGBA" == reloaded.mode
        assert (32, 32) == reloaded.size
        assert reloaded.format == "ICO"
        im = hopper(mode).resize((32, 32), Image.LANCZOS).convert("RGBA")
        assert_image_equal(reloaded, im)


def test_incorrect_size():
    with Image.open(TEST_ICO_FILE) as im:
        with pytest.raises(ValueError):
            im.size = (1, 1)


def test_save_256x256(tmp_path):
    """Issue #2264 https://github.com/python-pillow/Pillow/issues/2264"""
    # Arrange
    with Image.open("Tests/images/hopper_256x256.ico") as im:
        outfile = str(tmp_path / "temp_saved_hopper_256x256.ico")

        # Act
        im.save(outfile)
    with Image.open(outfile) as im_saved:

        # Assert
        assert im_saved.size == (256, 256)


def test_only_save_relevant_sizes(tmp_path):
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


def test_save_append_images(tmp_path):
    # append_images should be used for scaled down versions of the image
    im = hopper("RGBA")
    provided_im = Image.new("RGBA", (32, 32), (255, 0, 0))
    outfile = str(tmp_path / "temp_saved_multi_icon.ico")
    im.save(outfile, sizes=[(32, 32), (128, 128)], append_images=[provided_im])

    with Image.open(outfile) as reread:
        assert_image_equal(reread, hopper("RGBA"))

        reread.size = (32, 32)
        assert_image_equal(reread, provided_im)


def test_unexpected_size():
    # This image has been manually hexedited to state that it is 16x32
    # while the image within is still 16x16
    def open():
        with Image.open("Tests/images/hopper_unexpected.ico") as im:
            assert im.size == (16, 16)

    pytest.warns(UserWarning, open)


def test_draw_reloaded(tmp_path):
    with Image.open(TEST_ICO_FILE) as im:
        outfile = str(tmp_path / "temp_saved_hopper_draw.ico")

        draw = ImageDraw.Draw(im)
        draw.line((0, 0) + im.size, "#f00")
        im.save(outfile)

    with Image.open(outfile) as im:
        assert_image_equal_tofile(im, "Tests/images/hopper_draw.ico")
