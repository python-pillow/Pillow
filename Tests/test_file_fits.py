from __future__ import annotations

import struct
from io import BytesIO

import pytest

from PIL import FitsImagePlugin, Image

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

TEST_FILE = "Tests/images/hopper.fits"


def test_open() -> None:
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert im.format == "FITS"
        assert im.size == (128, 128)
        assert im.mode == "L"

        assert_image_equal(im, hopper("L"))


def test_gzip1() -> None:
    with Image.open("Tests/images/m13_gzip.fits") as im:
        assert im.getpixel((0, 0)) == 111

        assert_image_equal_tofile(im, "Tests/images/m13.fits")


def test_gzip_decode() -> None:
    with open("Tests/images/m13_gzip.fits", "rb") as fp:
        data = bytearray(fp.read())

    offset = 11040
    data[offset + 10] = 0
    with Image.open(BytesIO(data)) as im:
        assert im.tile[0].offset == offset
        with pytest.raises(OSError, match="Corrupt FITS gzip data"):
            im.load()

    data = data[: offset + 2]
    with Image.open(BytesIO(data)) as im:
        with pytest.raises(OSError, match="Truncated FITS gzip data"):
            im.load()


def test_invalid_file() -> None:
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act / Assert
    with pytest.raises(SyntaxError):
        FitsImagePlugin.FitsImageFile(invalid_file)


def test_unsupported_number_of_bits() -> None:
    b = BytesIO(
        b"".join(
            data.ljust(80, b" ")
            for data in [
                b"SIMPLE  = T",
                b"BITPIX  = 128",
                b"NAXIS   = 1",
                b"NAXIS1  = 0",
                b"END",
            ]
        )
    )
    with pytest.raises(OSError, match="Unsupported number of bits"):
        Image.open(b)


def test_truncated_fits() -> None:
    # No END to headers
    image_data = b"SIMPLE  =                    T" + b" " * 50 + b"TRUNCATE"
    with pytest.raises(OSError):
        FitsImagePlugin.FitsImageFile(BytesIO(image_data))


def test_naxis_zero() -> None:
    b = BytesIO(
        b"".join(
            data.ljust(80, b" ") for data in [b"SIMPLE  = T", b"NAXIS   = 0", b"END"]
        ).ljust(2881)
    )
    with pytest.raises(ValueError, match="No image data"):
        Image.open(b)


def test_comment() -> None:
    image_data = b"SIMPLE  =                    T / comment string"
    with pytest.raises(OSError):
        FitsImagePlugin.FitsImageFile(BytesIO(image_data))


def fits_image(bitpix: int, values: list[int], extra: list[str] = []) -> bytes:
    cards = [
        "SIMPLE  =                    T",
        "BITPIX  = %20d" % bitpix,
        "NAXIS   =                    2",
        "NAXIS1  = %20d" % len(values),
        "NAXIS2  =                    1",
        *extra,
        "END",
    ]
    header = b"".join(c.ljust(80).encode() for c in cards)
    header += b" " * (-len(header) % 2880)
    data = struct.pack(
        ">%d%s" % (len(values), {8: "B", 16: "h", 32: "i"}[bitpix]), *values
    )
    return header + data + b"\0" * (-len(data) % 2880)


def test_16bit_is_signed() -> None:
    # FITS 16-bit integers are signed
    with Image.open(BytesIO(fits_image(16, [-32768, -1, 0, 1, 32767]))) as im:
        assert im.mode == "I"
        assert [im.getpixel((x, 0)) for x in range(im.width)] == [
            -32768,
            -1,
            0,
            1,
            32767,
        ]


def test_16bit_scaling_keywords_in_info() -> None:
    # Unsigned 16-bit data is stored as signed with BZERO=32768;
    # the scaling keywords are exposed without being applied
    with Image.open(
        BytesIO(
            fits_image(
                16, [-32768, -32767, -1, 0, 32767], ["BZERO   =                32768"]
            )
        )
    ) as im:
        assert im.mode == "I"
        assert im.info["BZERO"] == 32768
        assert [im.getpixel((x, 0)) for x in range(im.width)] == [
            -32768,
            -32767,
            -1,
            0,
            32767,
        ]


def test_bscale_keyword_in_info() -> None:
    with Image.open(
        BytesIO(
            fits_image(
                16,
                [-32768, -1, 0, 1, 32767],
                ["BSCALE  = 0.5", "BZERO   =                100"],
            )
        )
    ) as im:
        assert im.info["BZERO"] == 100
        assert im.info["BSCALE"] == 0.5
