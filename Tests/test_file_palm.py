from __future__ import annotations

import os.path
import subprocess

import pytest

from PIL import Image

from .helper import assert_image_equal, assert_image_similar, hopper, magick_command

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


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


def roundtrip(tmp_path: Path, im: Image.Image, **options: Any) -> Image.Image:
    magick = magick_command()
    if not magick:
        pytest.skip("ImageMagick not available")

    outfile = str(tmp_path / "temp.palm")

    im.save(outfile, **options)
    return open_with_magick(magick, tmp_path, outfile)


def test_monochrome(tmp_path: Path) -> None:
    helper_save_as_palm(tmp_path, "1")

    im = hopper("1")
    assert_image_equal(roundtrip(tmp_path, im), im)


def test_p_mode(tmp_path: Path) -> None:
    helper_save_as_palm(tmp_path, "P")

    im = hopper("P")
    converted = roundtrip(tmp_path, im)
    assert converted.mode == "P"
    assert_image_equal(converted.convert("RGB"), im.convert("RGB"))


@pytest.mark.parametrize("bpp", (1, 2, 4))
@pytest.mark.parametrize("info", (True, False))
def test_l_mode(tmp_path: Path, bpp: int, info: bool) -> None:
    im = hopper("L")
    if info:
        reloaded = roundtrip(tmp_path, im, bpp=bpp)
    else:
        im.info["bpp"] = bpp
        reloaded = roundtrip(tmp_path, im)
    if bpp == 1:
        assert reloaded.mode == "1"
    else:
        assert reloaded.mode == "L"
        if info:
            assert_image_similar(reloaded, im, 23 if bpp == 2 else 6)


@pytest.mark.parametrize("mode", ("L", "RGB"))
def test_oserror(tmp_path: Path, mode: str) -> None:
    with pytest.raises(OSError):
        helper_save_as_palm(tmp_path, mode)
