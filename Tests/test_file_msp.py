from __future__ import annotations

import os
from pathlib import Path

import pytest

from PIL import Image, MspImagePlugin

from .helper import assert_image_equal, assert_image_equal_tofile, hopper

TEST_FILE = "Tests/images/hopper.msp"
EXTRA_DIR = "Tests/images/picins"
YA_EXTRA_DIR = "Tests/images/msp"


def test_sanity(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.msp"

    hopper("1").save(test_file)

    with Image.open(test_file) as im:
        im.load()
        assert im.mode == "1"
        assert im.size == (128, 128)
        assert im.format == "MSP"


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        MspImagePlugin.MspImageFile(invalid_file)


def test_bad_checksum() -> None:
    # Arrange
    # This was created by forcing Pillow to save with checksum=0
    bad_checksum = "Tests/images/hopper_bad_checksum.msp"

    # Act / Assert
    with pytest.raises(SyntaxError):
        MspImagePlugin.MspImageFile(bad_checksum)


def test_open_windows_v1() -> None:
    # Arrange
    # Act
    with Image.open(TEST_FILE) as im:
        # Assert
        assert_image_equal(im, hopper("1"))
        assert isinstance(im, MspImagePlugin.MspImageFile)


def _assert_file_image_equal(source_path: str, target_path: str) -> None:
    with Image.open(source_path) as im:
        assert_image_equal_tofile(im, target_path)


@pytest.mark.skipif(
    not os.path.exists(EXTRA_DIR), reason="Extra image files not installed"
)
def test_open_windows_v2() -> None:
    files = (
        os.path.join(EXTRA_DIR, f)
        for f in os.listdir(EXTRA_DIR)
        if os.path.splitext(f)[1] == ".msp"
    )
    for path in files:
        _assert_file_image_equal(path, path.replace(".msp", ".png"))


@pytest.mark.skipif(
    not os.path.exists(YA_EXTRA_DIR), reason="Even More Extra image files not installed"
)
def test_msp_v2() -> None:
    for f in os.listdir(YA_EXTRA_DIR):
        if ".MSP" not in f:
            continue
        path = os.path.join(YA_EXTRA_DIR, f)
        _assert_file_image_equal(path, path.replace(".MSP", ".png"))


def test_cannot_save_wrong_mode(tmp_path: Path) -> None:
    # Arrange
    im = hopper()
    filename = tmp_path / "temp.msp"

    # Act/Assert
    with pytest.raises(OSError):
        im.save(filename)
