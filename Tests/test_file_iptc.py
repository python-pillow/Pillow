from __future__ import annotations

import sys
from io import BytesIO, StringIO

import pytest

from PIL import Image, IptcImagePlugin, TiffImagePlugin, TiffTags

from .helper import assert_image_equal, hopper

TEST_FILE = "Tests/images/iptc.jpg"


def test_open() -> None:
    expected = Image.new("L", (1, 1))

    f = BytesIO(
        b"\x1c\x03<\x00\x02\x01\x00\x1c\x03x\x00\x01\x01\x1c\x03\x14\x00\x01\x01"
        b"\x1c\x03\x1e\x00\x01\x01\x1c\x08\n\x00\x01\x00"
    )
    with Image.open(f) as im:
        assert im.tile == [("iptc", (0, 0, 1, 1), 25, "raw")]
        assert_image_equal(im, expected)

    with Image.open(f) as im:
        assert im.load() is not None


def test_getiptcinfo_jpg_none() -> None:
    # Arrange
    with hopper() as im:
        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert iptc is None


def test_getiptcinfo_jpg_found() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert isinstance(iptc, dict)
    assert iptc[(2, 90)] == b"Budapest"
    assert iptc[(2, 101)] == b"Hungary"


def test_getiptcinfo_fotostation() -> None:
    # Arrange
    with open(TEST_FILE, "rb") as fp:
        data = bytearray(fp.read())
    data[86] = 240
    f = BytesIO(data)
    with Image.open(f) as im:
        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert iptc is not None
    assert 240 in (tag[0] for tag in iptc.keys()), "FotoStation tag not found"


def test_getiptcinfo_zero_padding() -> None:
    # Arrange
    with Image.open(TEST_FILE) as im:
        im.info["photoshop"][0x0404] += b"\x00\x00\x00"

        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert isinstance(iptc, dict)
    assert len(iptc) == 3


def test_getiptcinfo_tiff() -> None:
    expected = {(1, 90): b"\x1b%G", (2, 0): b"\xcf\xc0"}

    with Image.open("Tests/images/hopper.Lab.tif") as im:
        iptc = IptcImagePlugin.getiptcinfo(im)

    assert iptc == expected

    # Test with LONG tag type
    with Image.open("Tests/images/hopper.Lab.tif") as im:
        im.tag_v2.tagtype[TiffImagePlugin.IPTC_NAA_CHUNK] = TiffTags.LONG
        iptc = IptcImagePlugin.getiptcinfo(im)

    assert iptc == expected


def test_getiptcinfo_tiff_none() -> None:
    # Arrange
    with Image.open("Tests/images/hopper.tif") as im:
        # Act
        iptc = IptcImagePlugin.getiptcinfo(im)

    # Assert
    assert iptc is None


def test_i() -> None:
    # Arrange
    c = b"a"

    # Act
    with pytest.warns(DeprecationWarning, match="IptcImagePlugin.i"):
        ret = IptcImagePlugin.i(c)

    # Assert
    assert ret == 97


def test_dump(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    c = b"abc"
    # Temporarily redirect stdout
    mystdout = StringIO()
    monkeypatch.setattr(sys, "stdout", mystdout)

    # Act
    with pytest.warns(DeprecationWarning, match="IptcImagePlugin.dump"):
        IptcImagePlugin.dump(c)

    # Assert
    assert mystdout.getvalue() == "61 62 63 \n"


def test_pad_deprecation() -> None:
    with pytest.warns(DeprecationWarning, match="IptcImagePlugin.PAD"):
        assert IptcImagePlugin.PAD == b"\0\0\0\0"
