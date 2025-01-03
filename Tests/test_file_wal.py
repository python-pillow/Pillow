from __future__ import annotations

from PIL import WalImageFile

from .helper import assert_image_equal_tofile

TEST_FILE = "Tests/images/hopper.wal"


def test_open() -> None:
    with WalImageFile.open(TEST_FILE) as im:
        assert im.format == "WAL"
        assert im.format_description == "Quake2 Texture"
        assert im.mode == "P"
        assert im.size == (128, 128)

        assert isinstance(im, WalImageFile.WalImageFile)

        assert_image_equal_tofile(im, "Tests/images/hopper_wal.png")


def test_load() -> None:
    with WalImageFile.open(TEST_FILE) as im:
        px = im.load()
        assert px is not None
        assert px[0, 0] == 122

        # Test again now that it has already been loaded once
        px = im.load()
        assert px is not None
        assert px[0, 0] == 122
