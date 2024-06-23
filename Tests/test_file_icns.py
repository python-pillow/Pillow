from __future__ import annotations

import io
import os
import struct
import warnings
from pathlib import Path

import pytest
from unittest.mock import Mock, patch
from PIL import IcnsImagePlugin, Image, _binary

from .helper import assert_image_equal, assert_image_similar_tofile, skip_unless_feature

# sample icon file
TEST_FILE = "Tests/images/pillow.icns"


def test_sanity() -> None:
    # Loading this icon by default should result in the largest size
    # (512x512@2x) being loaded
    with Image.open(TEST_FILE) as im:
        # Assert that there is no unclosed file warning
        with warnings.catch_warnings():
            im.load()

        assert im.mode == "RGBA"
        assert im.size == (1024, 1024)
        assert im.format == "ICNS"


def test_load() -> None:
    with Image.open(TEST_FILE) as im:
        assert im.load()[0, 0] == (0, 0, 0, 0)

        # Test again now that it has already been loaded once
        assert im.load()[0, 0] == (0, 0, 0, 0)


def test_save(tmp_path: Path) -> None:
    temp_file = str(tmp_path / "temp.icns")

    with Image.open(TEST_FILE) as im:
        im.save(temp_file)

    with Image.open(temp_file) as reread:
        assert reread.mode == "RGBA"
        assert reread.size == (1024, 1024)
        assert reread.format == "ICNS"

    file_length = os.path.getsize(temp_file)
    with open(temp_file, "rb") as fp:
        fp.seek(4)
        assert _binary.i32be(fp.read(4)) == file_length


def test_save_append_images(tmp_path: Path) -> None:
    temp_file = str(tmp_path / "temp.icns")
    provided_im = Image.new("RGBA", (32, 32), (255, 0, 0, 128))

    with Image.open(TEST_FILE) as im:
        im.save(temp_file, append_images=[provided_im])

        assert_image_similar_tofile(im, temp_file, 1)

        with Image.open(temp_file) as reread:
            reread.size = (16, 16, 2)
            reread.load()
            assert_image_equal(reread, provided_im)


def test_save_fp() -> None:
    fp = io.BytesIO()

    with Image.open(TEST_FILE) as im:
        im.save(fp, format="ICNS")

    with Image.open(fp) as reread:
        assert reread.mode == "RGBA"
        assert reread.size == (1024, 1024)
        assert reread.format == "ICNS"


def test_sizes() -> None:
    # Check that we can load all of the sizes, and that the final pixel
    # dimensions are as expected
    with Image.open(TEST_FILE) as im:
        for w, h, r in im.info["sizes"]:
            wr = w * r
            hr = h * r
            im.size = (w, h, r)
            im.load()
            assert im.mode == "RGBA"
            assert im.size == (wr, hr)

        # Check that we cannot load an incorrect size
        with pytest.raises(ValueError):
            im.size = (1, 1)


def test_older_icon() -> None:
    # This icon was made with Icon Composer rather than iconutil; it still
    # uses PNG rather than JP2, however (since it was made on 10.9).
    with Image.open("Tests/images/pillow2.icns") as im:
        for w, h, r in im.info["sizes"]:
            wr = w * r
            hr = h * r
            with Image.open("Tests/images/pillow2.icns") as im2:
                im2.size = (w, h, r)
                im2.load()
                assert im2.mode == "RGBA"
                assert im2.size == (wr, hr)


@skip_unless_feature("jpg_2000")
def test_jp2_icon() -> None:
    # This icon uses JPEG 2000 images instead of the PNG images.
    # The advantage of doing this is that OS X 10.5 supports JPEG 2000
    # but not PNG; some commercial software therefore does just this.

    with Image.open("Tests/images/pillow3.icns") as im:
        for w, h, r in im.info["sizes"]:
            wr = w * r
            hr = h * r
            with Image.open("Tests/images/pillow3.icns") as im2:
                im2.size = (w, h, r)
                im2.load()
                assert im2.mode == "RGBA"
                assert im2.size == (wr, hr)


def test_getimage() -> None:
    with open(TEST_FILE, "rb") as fp:
        icns_file = IcnsImagePlugin.IcnsFile(fp)

        im = icns_file.getimage()
        assert im.mode == "RGBA"
        assert im.size == (1024, 1024)

        im = icns_file.getimage((512, 512))
        assert im.mode == "RGBA"
        assert im.size == (512, 512)


def test_not_an_icns_file() -> None:
    with io.BytesIO(b"invalid\n") as fp:
        with pytest.raises(SyntaxError):
            IcnsImagePlugin.IcnsFile(fp)


@skip_unless_feature("jpg_2000")
def test_icns_decompression_bomb() -> None:
    with Image.open(
        "Tests/images/oom-8ed3316a4109213ca96fb8a256a0bfefdece1461.icns"
    ) as im:
        with pytest.raises(Image.DecompressionBombError):
            im.load()

def test_read_32t():
    # Create a mock instance of a file-like object
    fobj = io.BytesIO()

    # Mock the file object to simulate normal execution
    fobj.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    fobj.seek(0)
    start_length = (0, 12)
    size = (1, 1, 1)
    result = IcnsImagePlugin.read_32t(fobj, start_length, size)
    assert isinstance(result, dict)

    # Simulate an exception
    fobj = io.BytesIO()
    fobj.write(b'\x01\x00\x00\x00')
    fobj.seek(0)
    with pytest.raises(SyntaxError, match="Unknown signature, expecting 0x00000000"):
        IcnsImagePlugin.read_32t(fobj, start_length, size)
