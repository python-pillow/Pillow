from __future__ import annotations

import tarfile
import warnings
from unittest.mock import patch

import pytest

from PIL import Image, TarIO, features

from .helper import is_pypy

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path

# Sample tar archive
TEST_TAR_FILE = "Tests/images/hopper.tar"


@pytest.mark.parametrize(
    "codec, test_path, format",
    (
        ("zlib", "hopper.png", "PNG"),
        ("jpg", "hopper.jpg", "JPEG"),
    ),
)
def test_sanity(codec: str, test_path: str, format: str) -> None:
    if features.check(codec):
        with TarIO.TarIO(TEST_TAR_FILE, test_path) as tar:
            with Image.open(tar) as im:
                im.load()
                assert im.mode == "RGB"
                assert im.size == (128, 128)
                assert im.format == format


def test_unexpected_end(tmp_path: Path) -> None:
    tmpfile = str(tmp_path / "temp.tar")
    with open(tmpfile, "w"):
        pass

    with pytest.raises(OSError, match="unexpected end of tar file"):
        with TarIO.TarIO(tmpfile, "test"):
            pass


def test_cannot_find_subfile() -> None:
    with pytest.raises(OSError, match="cannot find subfile"):
        with TarIO.TarIO(TEST_TAR_FILE, "test"):
            pass


@pytest.mark.parametrize(
    "field, value, exception",
    (
        (slice(0, 1), b"\xff", UnicodeDecodeError),
        (slice(124, 135), b"invalidsize", ValueError),
        (slice(124, 135), b"-1".rjust(11), ValueError),
    ),
)
@pytest.mark.parametrize("preceding_member", (False, True))
def test_invalid_header_closes_file(
    tmp_path: Path,
    field: slice,
    value: bytes,
    exception: type[Exception],
    preceding_member: bool,
) -> None:
    header = bytearray(tarfile.TarInfo("image.png").tobuf())
    header[field] = value
    tmpfile = tmp_path / "invalid.tar"
    prefix = tarfile.TarInfo("other.png").tobuf() if preceding_member else b""
    tmpfile.write_bytes(prefix + header)

    with open(tmpfile, "rb") as fh:
        with patch("PIL.TarIO.open", return_value=fh):
            with pytest.raises(exception):
                TarIO.TarIO(str(tmpfile), "image.png")
        assert fh.closed


@pytest.mark.parametrize(
    "operation, member",
    (("read", "hopper.png"), ("seek", "missing.png"), ("seek", "hopper.png")),
)
@pytest.mark.parametrize("exception", (OSError, KeyboardInterrupt))
def test_io_error_closes_file(
    operation: str, member: str, exception: type[BaseException]
) -> None:
    error = exception("TAR I/O failed")
    with open(TEST_TAR_FILE, "rb") as fh:
        with patch("PIL.TarIO.open", return_value=fh):
            with patch.object(fh, operation, side_effect=error):
                with pytest.raises(exception) as exc:
                    TarIO.TarIO(TEST_TAR_FILE, member)
        assert exc.value is error
        assert fh.closed


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    with pytest.warns(ResourceWarning):
        TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")


def test_close() -> None:
    with warnings.catch_warnings(action="error"):
        tar = TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")
        tar.close()


def test_contextmanager() -> None:
    with warnings.catch_warnings(action="error"):
        with TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg") as tar:
            assert not tar.fh.closed
            assert tar.read(2) == b"\xff\xd8"
        assert tar.fh.closed


@pytest.mark.parametrize("size", (b"-1", b"-512"))
def test_odd(tmp_path: Path, size: bytes) -> None:
    with open(TEST_TAR_FILE, "rb") as f:
        data = bytearray(f.read())

    data[124:135] = size.rjust(11)

    tmpfile = tmp_path / "temp.tar"
    tmpfile.write_bytes(data)

    with pytest.raises(ValueError, match="size must not be negative"):
        TarIO.TarIO(str(tmpfile), "test")


def test_zero_length_member(tmp_path: Path) -> None:
    # A zero-length member is legal: members stored after it must still be found
    tmpfile = tmp_path / "temp.tar"
    with tarfile.open(tmpfile, "w") as tar:
        tar.addfile(tarfile.TarInfo("empty.txt"))
        tar.add("Tests/images/hopper.jpg", "hopper.jpg")

    with TarIO.TarIO(str(tmpfile), "hopper.jpg") as tar:
        with Image.open(tar) as im:
            im.load()
            assert im.size == (128, 128)
