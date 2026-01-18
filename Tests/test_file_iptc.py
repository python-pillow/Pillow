from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image, IptcImagePlugin, TiffImagePlugin, TiffTags

from .helper import assert_image_equal

TEST_FILE = "Tests/images/iptc.jpg"


def create_iptc_image(info: dict[str, int] = {}) -> BytesIO:
    def field(tag: tuple[int, int], value: bytes) -> bytes:
        return bytes((0x1C,) + tag + (0, len(value))) + value

    data = field((3, 60), bytes((info.get("layers", 1), info.get("component", 0))))
    data += field((3, 120), bytes((info.get("compression", 1),)))
    if "band" in info:
        data += field((3, 65), bytes((info["band"] + 1,)))
    data += field((3, 20), b"\x01")  # width
    data += field((3, 30), b"\x01")  # height
    data += field(
        (8, 10),
        bytes((info.get("data", 0),)),
    )

    return BytesIO(data)


def test_open() -> None:
    expected = Image.new("L", (1, 1))

    f = create_iptc_image()
    with Image.open(f) as im:
        assert im.tile == [("iptc", (0, 0, 1, 1), 25, ("raw", None))]
        assert_image_equal(im, expected)

    with Image.open(f) as im:
        assert im.load() is not None


def test_field_length() -> None:
    f = create_iptc_image()
    f.seek(28)
    f.write(b"\xff")
    with pytest.raises(OSError, match="illegal field length in IPTC/NAA file"):
        with Image.open(f):
            pass


@pytest.mark.parametrize("layers, mode", ((3, "RGB"), (4, "CMYK")))
def test_layers(layers: int, mode: str) -> None:
    for band in range(-1, layers):
        info = {"layers": layers, "component": 1, "data": 5}
        if band != -1:
            info["band"] = band
        f = create_iptc_image(info)
        with Image.open(f) as im:
            assert im.mode == mode

            data = [0] * layers
            data[max(band, 0)] = 5
            assert im.getpixel((0, 0)) == tuple(data)


def test_unknown_compression() -> None:
    f = create_iptc_image({"compression": 2})
    with pytest.raises(OSError, match="Unknown IPTC image compression"):
        with Image.open(f):
            pass


def test_getiptcinfo() -> None:
    f = create_iptc_image()
    with Image.open(f) as im:
        assert IptcImagePlugin.getiptcinfo(im) == {
            (3, 60): b"\x01\x00",
            (3, 120): b"\x01",
            (3, 20): b"\x01",
            (3, 30): b"\x01",
        }


def test_getiptcinfo_jpg_none() -> None:
    # Arrange
    with Image.open("Tests/images/hopper.jpg") as im:
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
        assert isinstance(im, TiffImagePlugin.TiffImageFile)
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
