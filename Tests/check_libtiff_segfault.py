import pytest

from PIL import Image

TEST_FILE = "Tests/images/libtiff_segfault.tif"


def test_libtiff_segfault():
    """This test should not segfault. It will on Pillow <= 3.1.0 and
    libtiff >= 4.0.0
    """

    with pytest.raises(OSError):
        with Image.open(TEST_FILE) as im:
            im.load()
