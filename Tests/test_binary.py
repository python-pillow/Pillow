from PIL import _binary


def test_standard():
    assert _binary.i8(b"*") == 42
    assert _binary.o8(42) == b"*"


def test_little_endian():
    assert _binary.i16le(b"\xff\xff\x00\x00") == 65535
    assert _binary.i32le(b"\xff\xff\x00\x00") == 65535

    assert _binary.o16le(65535) == b"\xff\xff"
    assert _binary.o32le(65535) == b"\xff\xff\x00\x00"


def test_big_endian():
    assert _binary.i16be(b"\x00\x00\xff\xff") == 0
    assert _binary.i32be(b"\x00\x00\xff\xff") == 65535

    assert _binary.o16be(65535) == b"\xff\xff"
    assert _binary.o32be(65535) == b"\x00\x00\xff\xff"
