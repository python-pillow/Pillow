from tester import *
import os.path


def helper_save_as_pdf(mode):
    # Arrange
    im = lena(mode)
    outfile = tempfile("temp_" + mode + ".pdf")

    # Act
    im.save(outfile)

    # Assert
    assert_true(os.path.isfile(outfile))
    assert_greater(os.path.getsize(outfile), 0)


def test_greyscale():
    # Arrange
    mode = "L"

    # Act / Assert
    helper_save_as_pdf(mode)


def test_rgb():
    # Arrange
    mode = "RGB"

    # Act / Assert
    helper_save_as_pdf(mode)


# FIXME: P-mode test fails on Python 3.
# https://travis-ci.org/hugovk/Pillow/builds/24915249
#   File "/home/travis/build/hugovk/Pillow/PIL/PdfImagePlugin.py", line 108, in _save
#     colorspace = colorspace + b"> ]"
# TypeError: Can't convert 'bytes' object to str implicitly
# def test_p_mode():
#     # Arrange
#     mode = "P"
#
#     # Act / Assert
#     helper_save_as_pdf(mode)


def test_cmyk_mode():
    # Arrange
    mode = "CMYK"

    # Act / Assert
    helper_save_as_pdf(mode)


# End of file
