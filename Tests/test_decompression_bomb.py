from tester import *

from PIL import Image

test_file = "Images/lena.ppm"


def test_no_warning_small_file():
    # Implicit assert: no warning.
    # A warning would cause a failure.
    Image.open(test_file)


def test_no_warning_no_limit():
    # Arrange
    # Turn limit off
    Image.MAX_IMAGE_PIXELS = None
    assert_equal(Image.MAX_IMAGE_PIXELS, None)

    # Act / Assert
    # Implicit assert: no warning.
    # A warning would cause a failure.
    Image.open(test_file)


def test_warning():
    # Arrange
    # Set limit to a low, easily testable value
    Image.MAX_IMAGE_PIXELS = 10
    assert_equal(Image.MAX_IMAGE_PIXELS, 10)

    # Act / Assert
    assert_warning(
        DecompressionBombWarning,
        lambda: Image.open(test_file))

# End of file
