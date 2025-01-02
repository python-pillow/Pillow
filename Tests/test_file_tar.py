from __future__ import annotations

import warnings

import pytest

from PIL import Image, TarIO, features

from .helper import is_pypy

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


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    with pytest.warns(ResourceWarning):
        TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")


def test_close() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        tar = TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")
        tar.close()


def test_contextmanager() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        with TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg"):
            pass
