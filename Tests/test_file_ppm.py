import sys
from io import BytesIO

import pytest

from PIL import Image

from .helper import assert_image_equal_tofile, assert_image_similar, hopper

# sample ppm stream
TEST_FILE = "Tests/images/hopper.ppm"


def test_sanity():
    with Image.open(TEST_FILE) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format, "PPM"
        assert im.get_format_mimetype() == "image/x-portable-pixmap"


def test_16bit_pgm():
    with Image.open("Tests/images/16_bit_binary.pgm") as im:
        im.load()
        assert im.mode == "I"
        assert im.size == (20, 100)
        assert im.get_format_mimetype() == "image/x-portable-graymap"

        assert_image_equal_tofile(im, "Tests/images/16_bit_binary_pgm.png")


def test_16bit_pgm_write(tmp_path):
    with Image.open("Tests/images/16_bit_binary.pgm") as im:
        im.load()

        f = str(tmp_path / "temp.pgm")
        im.save(f, "PPM")

        assert_image_equal_tofile(im, f)


def test_pnm(tmp_path):
    with Image.open("Tests/images/hopper.pnm") as im:
        assert_image_similar(im, hopper(), 0.0001)

        f = str(tmp_path / "temp.pnm")
        im.save(f)

        assert_image_equal_tofile(im, f)


def test_truncated_file(tmp_path):
    path = str(tmp_path / "temp.pgm")
    with open(path, "w") as f:
        f.write("P6")

    with pytest.raises(ValueError):
        with Image.open(path):
            pass


def test_neg_ppm():
    # Storage.c accepted negative values for xsize, ysize.  the
    # internal open_ppm function didn't check for sanity but it
    # has been removed. The default opener doesn't accept negative
    # sizes.

    with pytest.raises(OSError):
        with Image.open("Tests/images/negative_size.ppm"):
            pass


def test_mimetypes(tmp_path):
    path = str(tmp_path / "temp.pgm")

    with open(path, "w") as f:
        f.write("P4\n128 128\n255")
    with Image.open(path) as im:
        assert im.get_format_mimetype() == "image/x-portable-bitmap"

    with open(path, "w") as f:
        f.write("PyCMYK\n128 128\n255")
    with Image.open(path) as im:
        assert im.get_format_mimetype() == "image/x-portable-anymap"


@pytest.mark.parametrize("buffer", (True, False))
def test_save_stdout(buffer):
    old_stdout = sys.stdout

    if buffer:

        class MyStdOut:
            buffer = BytesIO()

        mystdout = MyStdOut()
    else:
        mystdout = BytesIO()

    sys.stdout = mystdout

    with Image.open(TEST_FILE) as im:
        im.save(sys.stdout, "PPM")

    # Reset stdout
    sys.stdout = old_stdout

    if buffer:
        mystdout = mystdout.buffer
    with Image.open(mystdout) as reloaded:
        assert_image_equal_tofile(reloaded, TEST_FILE)
