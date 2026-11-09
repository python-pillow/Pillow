from __future__ import annotations

from io import BytesIO

import pytest

from PIL import FitsImagePlugin, Image, ImageFile

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


def test_rice1() -> None:
    # https://fits.gsfc.nasa.gov/registry/tilecompression/m13_rice.fits
    with Image.open("Tests/images/m13_rice.fits") as im:
        assert im.mode == "I"
        with Image.open("Tests/images/m13.fits") as reference:
            assert_image_equal(im, reference.convert("I"))


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


def rice_fits(
    payloads: list[bytes],
    bitpix: int = 8,
    size: tuple[int, int] = (4, 1),
    tile_size: tuple[int, int] | None = None,
    bytepix: int | None = 1,
    descriptor: str = "P",
    heap_gap: int = 0,
    extra_column: bool = False,
    headers: dict[str, str | int] | None = None,
) -> bytes:
    def header_unit(values: dict[str, str | int]) -> bytes:
        return (
            b"".join(
                f"{key:8}= {value}".encode().ljust(80) for key, value in values.items()
            )
            + b"END".ljust(80)
        ).ljust(2880, b" ")

    primary = header_unit({"SIMPLE": "T", "BITPIX": 8, "NAXIS": 0})
    descriptor_width = 4 if descriptor == "P" else 8
    row_size = descriptor_width * 2 + (2 if extra_column else 0)
    values: dict[str, str | int] = {
        "XTENSION": "'BINTABLE'",
        "BITPIX": 8,
        "NAXIS": 2,
        "NAXIS1": row_size,
        "NAXIS2": len(payloads),
        "PCOUNT": sum(map(len, payloads)) + heap_gap,
        "GCOUNT": 1,
        "TFIELDS": 2 if extra_column else 1,
        "ZIMAGE": "T",
        "ZCMPTYPE": "'RICE_1  '",
        "ZBITPIX": bitpix,
        "ZNAXIS": 2,
        "ZNAXIS1": size[0],
        "ZNAXIS2": size[1],
    }
    column = 2 if extra_column else 1
    if extra_column:
        values.update({"TTYPE1": "'IGNORED'", "TFORM1": "'9X'"})
    values[f"TTYPE{column}"] = "'COMPRESSED_DATA'"
    values[f"TFORM{column}"] = f"'1{descriptor}B({max(map(len, payloads))})'"
    if tile_size is not None:
        values.update({"ZTILE1": tile_size[0], "ZTILE2": tile_size[1]})
    if bytepix is not None:
        values.update({"ZNAME1": "'BYTEPIX '", "ZVAL1": bytepix})
    if heap_gap:
        values["THEAP"] = row_size * len(payloads) + heap_gap
    if headers:
        values.update(headers)
    rows = bytearray()
    offset = 0
    for payload in payloads:
        if extra_column:
            rows += b"\x00\x00"
        rows += len(payload).to_bytes(descriptor_width, "big")
        rows += offset.to_bytes(descriptor_width, "big")
        offset += len(payload)
    data = bytes(rows) + bytes(heap_gap) + b"".join(payloads)
    return primary + header_unit(values) + data


@pytest.mark.parametrize(
    "bitpix,bytepix,payload,expected,mode",
    [
        (8, 1, b"\x07\x00", 7, "L"),
        (16, 2, b"\xff\xff\x00", -1, "I"),
        (32, 4, b"\x80\x00\x00\x00\x00", -(2**31), "I"),
        (16, None, b"\xff\xff\xff\xff\x00", -1, "I"),
    ],
)
def test_rice_constant(
    bitpix: int, bytepix: int | None, payload: bytes, expected: int, mode: str
) -> None:
    with Image.open(BytesIO(rice_fits([payload], bitpix, bytepix=bytepix))) as im:
        assert im.mode == mode
        assert im.size == (4, 1)
        assert list(im.get_flattened_data()) == [expected] * 4


@pytest.mark.parametrize("descriptor", ["P", "Q"])
@pytest.mark.parametrize("extra_column", [False, True])
def test_rice_tiles(descriptor: str, extra_column: bool) -> None:
    data = rice_fits(
        [b"\x01\x00", b"\x02\x00", b"\x03\x00", b"\x04\x00"],
        size=(5, 3),
        tile_size=(3, 2),
        descriptor=descriptor,
        heap_gap=19,
        extra_column=extra_column,
    )
    with Image.open(BytesIO(data)) as im:
        assert im.size == (5, 3)
        assert list(im.get_flattened_data()) == [
            3,
            3,
            3,
            4,
            4,
            1,
            1,
            1,
            2,
            2,
            1,
            1,
            1,
            2,
            2,
        ]


def test_rice_one_dimension() -> None:
    data = rice_fits(
        [b"\x01\x00", b"\x02\x00"], size=(5, 1), tile_size=(3, 1), headers={"ZNAXIS": 1}
    )
    with Image.open(BytesIO(data)) as im:
        assert im.size == (1, 5)
        assert list(im.get_flattened_data()) == [2, 2, 1, 1, 1]


# Produced with Astropy 8.0.2's CFITSIO-backed Rice1 codec, BLOCKSIZE=32.
# The 33 samples cross a block boundary without byte alignment.
@pytest.mark.parametrize(
    "bytepix,encoded",
    [
        (1, "0032492492492492492492492492"),
        (2, "00001924924924924924924924924480"),
        (4, "000000000c92492492492492492492492120"),
    ],
)
@pytest.mark.parametrize("chunk_size", [1, 2, 7, 65536])
def test_rice_ramp(
    bytepix: int, encoded: str, chunk_size: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ImageFile, "MAXBLOCK", chunk_size)
    data = rice_fits([bytes.fromhex(encoded)], bytepix * 8, (11, 3), (11, 3), bytepix)
    with Image.open(BytesIO(data)) as im:
        assert list(im.get_flattened_data()) == list(range(22, 33)) + list(
            range(11, 22)
        ) + list(range(11))


@pytest.mark.parametrize(
    "bytepix,encoded",
    [
        (1, "80e0003fe0405fc03fe0405fc03fe0405fc03fe0405fc03fe0405fc03fe0405fc03ffc"),
        (
            2,
            (
                "8000f00000001ffff00020002fffe0001ffff00020002fffe0001ffff00020002"
                "fffe0001ffff00020002fffe0001ffff00020002fffe0001ffff00020002fffe0001fffff"
            ),
        ),
        (
            4,
            (
                "80000000d0000000000000000ffffffff80000001000000017fffffff00000000"
                "ffffffff80000001000000017fffffff00000000ffffffff80000001000000017fffffff00000000"
                "ffffffff80000001000000017fffffff00000000ffffffff80000001000000017fffffff00000000"
                "ffffffff80000001000000017fffffff00000000ebfffffffc0"
            ),
        ),
    ],
)
def test_rice_signed_wraparound(
    bytepix: int, encoded: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(ImageFile, "MAXBLOCK", 1)
    limit = 1 << (bytepix * 8 - 1)
    expected = ([-limit, limit - 1, -1, 0, 1] * 7)[:33]
    if bytepix == 1:
        expected = [value & 255 for value in expected]
    data = rice_fits([bytes.fromhex(encoded)], bytepix * 8, (33, 1), bytepix=bytepix)
    with Image.open(BytesIO(data)) as im:
        assert list(im.get_flattened_data()) == expected


def test_rice_unordered_heap() -> None:
    data = bytearray(rice_fits([b"\x01\x00", b"\x02\x00"], size=(4, 2)))
    data[5760:5768], data[5768:5776] = data[5768:5776], data[5760:5768]
    with Image.open(BytesIO(data)) as im:
        assert list(im.get_flattened_data()) == [1] * 4 + [2] * 4


def test_rice_nondefault_blocksize() -> None:
    # Two all-zero-difference blocks, each containing three samples.
    data = rice_fits(
        [b"\x07\x00"],
        size=(6, 1),
        headers={"ZNAME2": "'BLOCKSIZE'", "ZVAL2": 3, "ZCMPTYPE": "'RICE_ONE'"},
    )
    with Image.open(BytesIO(data)) as im:
        assert list(im.get_flattened_data()) == [7] * 6


@pytest.mark.parametrize(
    "headers,message",
    [
        ({"ZBITPIX": -32}, "pixel type"),
        ({"ZBITPIX": 64}, "pixel type"),
        ({"ZNAXIS": 3}, "dimensions"),
        ({"ZNAXIS1": -1}, "image size"),
        ({"ZTILE1": 0}, "tile size"),
        ({"ZTILE2": -1}, "tile size"),
        ({"ZTILE1": 3}, "tile count"),
        ({"NAXIS1": 0}, "heap"),
        ({"NAXIS2": 0}, "heap"),
        ({"THEAP": 0}, "heap"),
        ({"PCOUNT": -1}, "heap"),
        ({"TFORM1": "'2PB'"}, "compressed data column"),
        ({"TFORM1": "'1PI'"}, "compressed data column"),
        ({"TFORM1": "'BOGUS'"}, "table column"),
        ({"TFORM1": "'1QB'"}, "table row"),
        ({"TTYPE1": "'NOT_COMPRESSED'"}, "table row"),
        ({"ZVAL1": 3}, "parameters"),
        ({"ZNAME2": "'BLOCKSIZE'", "ZVAL2": 0}, "parameters"),
        ({"ZNAME2": "'BLOCKSIZE'", "ZVAL2": 2**31}, "parameters"),
    ],
)
def test_rice_invalid_headers(headers: dict[str, str | int], message: str) -> None:
    with pytest.raises(OSError, match=message):
        FitsImagePlugin.FitsImageFile(
            BytesIO(rice_fits([b"\x07\x00"], headers=headers))
        )


@pytest.mark.parametrize("length,offset", [(0, 0), (3, 0), (2, -1), (1, 2), (-1, 0)])
def test_rice_invalid_descriptor(length: int, offset: int) -> None:
    data = bytearray(rice_fits([b"\x07\x00"]))
    data[5760:5768] = length.to_bytes(4, "big", signed=True) + offset.to_bytes(
        4, "big", signed=True
    )
    with pytest.raises(OSError, match="tile descriptor"):
        Image.open(BytesIO(data))


def test_rice_truncated_table() -> None:
    data = rice_fits([b"\x07\x00"])
    with pytest.raises(OSError, match="Truncated File Read"):
        Image.open(BytesIO(data[:5767]))


@pytest.mark.parametrize(
    "payload", [b"\x07", b"\x07\x20", b"\x07\xe0", b"\x07\x20\x00"]
)
def test_rice_truncated_data(payload: bytes) -> None:
    with Image.open(BytesIO(rice_fits([payload]))) as im:
        with pytest.raises(OSError):
            im.load()


@pytest.mark.parametrize("bad_tile", [0, 1])
@pytest.mark.parametrize("payload", [b"\x07", b"\x07\x20"])
def test_rice_invalid_tile(bad_tile: int, payload: bytes) -> None:
    payloads = [b"\x08\x00", b"\x08\x00"]
    payloads[bad_tile] = payload
    with Image.open(BytesIO(rice_fits(payloads, size=(4, 2)))) as im:
        with pytest.raises(OSError, match="Corrupt FITS Rice data"):
            im.load()


def test_rice_missing_payload() -> None:
    data = rice_fits([b"\x07\x00"])
    with Image.open(BytesIO(data[:-2])) as im:
        with pytest.raises(OSError, match="Truncated FITS Rice data"):
            im.load()


@pytest.mark.parametrize("identifier", range(27, 32))
def test_rice_reserved_block(identifier: int) -> None:
    payload = bytes(4) + bytes([identifier << 3])
    with Image.open(BytesIO(rice_fits([payload], 32, bytepix=4))) as im:
        with pytest.raises(OSError, match="Corrupt FITS Rice data"):
            im.load()


@pytest.mark.parametrize(
    "mode,rawmode,bytepix,blocksize,length",
    [
        ("RGB", "RGB", 1, 32, 2),
        ("I", "I;32BS", 1, 32, 2),
        ("L", "L", 3, 32, 2),
        ("L", "L", 1, 0, 2),
        ("L", "L", 1, -1, 2),
        ("L", "L", 1, 32, 0),
    ],
)
def test_rice_decoder_parameters(
    mode: str, rawmode: str, bytepix: int, blocksize: int, length: int
) -> None:
    with pytest.raises(ValueError):
        Image._getdecoder(mode, "fits_rice", (rawmode, bytepix, blocksize, length))
