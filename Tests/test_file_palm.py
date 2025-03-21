from __future__ import annotations

import os.path
import subprocess
from pathlib import Path

import pytest

from PIL import Image

from .helper import assert_image_equal, hopper, magick_command


def helper_save_as_palm(tmp_path: Path, mode: str) -> None:
    # Arrange
    im = hopper(mode)
    outfile = tmp_path / ("temp_" + mode + ".palm")

    # Act
    im.save(outfile)

    # Assert
    assert os.path.isfile(outfile)
    assert os.path.getsize(outfile) > 0


def open_with_magick(magick: list[str], tmp_path: Path, f: str) -> Image.Image:
    outfile = tmp_path / "temp.png"
    rc = subprocess.call(
        magick + [f, outfile], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    assert not rc
    return Image.open(outfile)


def roundtrip(tmp_path: Path, mode: str) -> None:
    magick = magick_command()
    if not magick:
        return

    im = hopper(mode)
    outfile = str(tmp_path / "temp.palm")

    im.save(outfile)
    converted = open_with_magick(magick, tmp_path, outfile)
    if mode == "P":
        assert converted.mode == "P"

        im = im.convert("RGB")
        converted = converted.convert("RGB")
    assert_image_equal(converted, im)


def test_monochrome(tmp_path: Path) -> None:
    # Arrange
    mode = "1"

    # Act / Assert
    helper_save_as_palm(tmp_path, mode)
    roundtrip(tmp_path, mode)


def test_p_mode(tmp_path: Path) -> None:
    # Arrange
    mode = "P"

    # Act / Assert
    helper_save_as_palm(tmp_path, mode)
    roundtrip(tmp_path, mode)


@pytest.mark.parametrize("mode", ("L", "RGB"))
def test_oserror(tmp_path: Path, mode: str) -> None:
    with pytest.raises(OSError):
        helper_save_as_palm(tmp_path, mode)
