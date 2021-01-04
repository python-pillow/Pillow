import sys
from io import StringIO

from PIL import Image, IptcImagePlugin

from .helper import hopper

TEST_FILE = "Tests/images/iptc.jpg"


def test_getiptcinfo_jpg_none():
    # Arrange
    with hopper() as im:

        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert iptc is None


def test_getiptcinfo_jpg_found():
    # Arrange
    with Image.open(TEST_FILE) as im:

        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert isinstance(iptc, dict)
    assert iptc[(2, 90)] == b"Budapest"
    assert iptc[(2, 101)] == b"Hungary"


def test_getiptcinfo_tiff_none():
    # Arrange
    with Image.open("Tests/images/hopper.tif") as im:

        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert iptc is None


def test_i():
    # Arrange
    c = b"a"

    # Act
    ret = IptcImagePlugin.i(c)

    # Assert
    assert ret == 97


def test_dump():
    # Arrange
    c = b"abc"
    # Temporarily redirect stdout
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    # Act
    IptcImagePlugin.dump(c)

    # Reset stdout
    sys.stdout = old_stdout

    # Assert
    assert mystdout.getvalue() == "61 62 63 \n"
