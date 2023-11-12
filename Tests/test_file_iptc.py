import sys
from io import BytesIO, StringIO

import pytest

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


def test_getiptcinfo_fotostation():
    # Arrange
    with open(TEST_FILE, "rb") as fp:
        data = bytearray(fp.read())
    data[86] = 240
    f = BytesIO(data)
    with Image.open(f) as im:
        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    for tag in iptc.keys():
        if tag[0] == 240:
            return
    pytest.fail("FotoStation tag not found")


def test_getiptcinfo_zero_padding():
    # Arrange
    with Image.open(TEST_FILE) as im:
        im.info["photoshop"][0x0404] += b"\x00\x00\x00"

        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert isinstance(iptc, dict)
    assert len(iptc) == 3


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
