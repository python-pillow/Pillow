import sys
from io import BytesIO

import pytest

from PIL import Image, UnidentifiedImageError

from .helper import assert_image_equal_tofile, assert_image_similar, hopper

# sample ppm stream
TEST_FILE = "Tests/images/hopper.ppm"


def test_sanity():
    with Image.open(TEST_FILE) as im:
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "PPM"
        assert im.get_format_mimetype() == "image/x-portable-pixmap"


@pytest.mark.parametrize(
    "data, mode, pixels",
    (
        (b"P5 3 1 4 \x00\x02\x04", "L", (0, 128, 255)),
        (b"P5 3 1 257 \x00\x00\x00\x80\x01\x01", "I", (0, 32640, 65535)),
        # P6 with maxval < 255
        (
            b"P6 3 1 17 \x00\x01\x02\x08\x09\x0A\x0F\x10\x11",
            "RGB",
            (
                (0, 15, 30),
                (120, 135, 150),
                (225, 240, 255),
            ),
        ),
        # P6 with maxval > 255
        # Scale down to 255, since there is no RGB mode with more than 8-bit
        (
            b"P6 3 1 257 \x00\x00\x00\x01\x00\x02"
            b"\x00\x80\x00\x81\x00\x82\x01\x00\x01\x01\xFF\xFF",
            "RGB",
            (
                (0, 1, 2),
                (127, 128, 129),
                (254, 255, 255),
            ),
        ),
    ),
)
def test_arbitrary_maxval(data, mode, pixels):
    fp = BytesIO(data)
    with Image.open(fp) as im:
        assert im.size == (3, 1)
        assert im.mode == mode

        px = im.load()
        assert tuple(px[x, 0] for x in range(3)) == pixels


def test_16bit_pgm():
    with Image.open("Tests/images/16_bit_binary.pgm") as im:
        assert im.mode == "I"
        assert im.size == (20, 100)
        assert im.get_format_mimetype() == "image/x-portable-graymap"

        assert_image_equal_tofile(im, "Tests/images/16_bit_binary_pgm.png")


def test_16bit_pgm_write(tmp_path):
    with Image.open("Tests/images/16_bit_binary.pgm") as im:
        f = str(tmp_path / "temp.pgm")
        im.save(f, "PPM")

        assert_image_equal_tofile(im, f)


def test_pnm(tmp_path):
    with Image.open("Tests/images/hopper.pnm") as im:
        assert_image_similar(im, hopper(), 0.0001)

        f = str(tmp_path / "temp.pnm")
        im.save(f)

        assert_image_equal_tofile(im, f)


def test_magic(tmp_path):
    path = str(tmp_path / "temp.ppm")
    with open(path, "wb") as f:
        f.write(b"PyInvalid")

    with pytest.raises(UnidentifiedImageError):
        with Image.open(path):
            pass


def test_header_with_comments(tmp_path):
    path = str(tmp_path / "temp.ppm")
    with open(path, "wb") as f:
        f.write(b"P6 #comment\n#comment\r12#comment\r8\n128 #comment\n255\n")

    with Image.open(path) as im:
        assert im.size == (128, 128)


def test_non_integer_token(tmp_path):
    path = str(tmp_path / "temp.ppm")
    with open(path, "wb") as f:
        f.write(b"P6\nTEST")

    with pytest.raises(ValueError):
        with Image.open(path):
            pass


def test_token_too_long(tmp_path):
    path = str(tmp_path / "temp.ppm")
    with open(path, "wb") as f:
        f.write(b"P6\n 01234567890")

    with pytest.raises(ValueError) as e:
        with Image.open(path):
            pass

    assert str(e.value) == "Token too long in file header: b'01234567890'"


def test_truncated_file(tmp_path):
    # Test EOF in header
    path = str(tmp_path / "temp.pgm")
    with open(path, "w") as f:
        f.write("P6")

    with pytest.raises(ValueError) as e:
        with Image.open(path):
            pass

    assert str(e.value) == "Reached EOF while reading header"

    # Test EOF for PyDecoder
    fp = BytesIO(b"P5 3 1 4")
    with Image.open(fp) as im:
        with pytest.raises(ValueError):
            im.load()


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
