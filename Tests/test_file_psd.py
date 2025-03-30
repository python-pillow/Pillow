from __future__ import annotations

import warnings

import pytest

from PIL import Image, PsdImagePlugin

from .helper import assert_image_equal_tofile, assert_image_similar, hopper, is_pypy

test_file = "Tests/images/hopper.psd"


def test_sanity() -> None:
    with Image.open(test_file) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "PSD"
        assert im.get_format_mimetype() == "image/vnd.adobe.photoshop"

        im2 = hopper()
        assert_image_similar(im, im2, 4.8)


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open_test_image() -> None:
        im = Image.open(test_file)
        im.load()

    with pytest.warns(ResourceWarning):
        open_test_image()


def test_closed_file() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        im = Image.open(test_file)
        im.load()
        im.close()


def test_context_manager() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        with Image.open(test_file) as im:
            im.load()


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        PsdImagePlugin.PsdImageFile(invalid_file)


def test_n_frames() -> None:
    with Image.open("Tests/images/hopper_merged.psd") as im:
        assert isinstance(im, PsdImagePlugin.PsdImageFile)
        assert im.n_frames == 1
        assert not im.is_animated

    for path in [test_file, "Tests/images/negative_layer_count.psd"]:
        with Image.open(path) as im:
            assert isinstance(im, PsdImagePlugin.PsdImageFile)
            assert im.n_frames == 2
            assert im.is_animated


def test_eoferror() -> None:
    with Image.open(test_file) as im:
        assert isinstance(im, PsdImagePlugin.PsdImageFile)

        # PSD seek index starts at 1 rather than 0
        n_frames = im.n_frames + 1

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_seek_tell() -> None:
    with Image.open(test_file) as im:
        layer_number = im.tell()
        assert layer_number == 1

        with pytest.raises(EOFError):
            im.seek(0)

        im.seek(1)
        layer_number = im.tell()
        assert layer_number == 1

        im.seek(2)
        layer_number = im.tell()
        assert layer_number == 2


def test_seek_eoferror() -> None:
    with Image.open(test_file) as im:
        with pytest.raises(EOFError):
            im.seek(-1)


def test_open_after_exclusive_load() -> None:
    with Image.open(test_file) as im:
        im.load()
        im.seek(im.tell() + 1)
        im.load()


def test_rgba() -> None:
    with Image.open("Tests/images/rgba.psd") as im:
        assert_image_equal_tofile(im, "Tests/images/imagedraw_square.png")


def test_negative_top_left_layer() -> None:
    with Image.open("Tests/images/negative_top_left_layer.psd") as im:
        assert isinstance(im, PsdImagePlugin.PsdImageFile)
        assert im.layers[0][2] == (-50, -50, 50, 50)


def test_layer_skip() -> None:
    with Image.open("Tests/images/five_channels.psd") as im:
        assert isinstance(im, PsdImagePlugin.PsdImageFile)
        assert im.n_frames == 1


def test_icc_profile() -> None:
    with Image.open(test_file) as im:
        assert "icc_profile" in im.info

        icc_profile = im.info["icc_profile"]
        assert len(icc_profile) == 3144


def test_no_icc_profile() -> None:
    with Image.open("Tests/images/hopper_merged.psd") as im:
        assert "icc_profile" not in im.info


def test_combined_larger_than_size() -> None:
    # The combined size of the individual parts is larger than the
    # declared 'size' of the extra data field, resulting in a backwards seek.

    # If we instead take the 'size' of the extra data field as the source of truth,
    # then the seek can't be negative
    with pytest.raises(OSError):
        with Image.open("Tests/images/combined_larger_than_size.psd"):
            pass


@pytest.mark.parametrize(
    "test_file,raises",
    [
        ("Tests/images/timeout-c8efc3fded6426986ba867a399791bae544f59bc.psd", OSError),
        ("Tests/images/timeout-dedc7a4ebd856d79b4359bbcc79e8ef231ce38f6.psd", OSError),
    ],
)
def test_crashes(test_file: str, raises: type[Exception]) -> None:
    with open(test_file, "rb") as f:
        with pytest.raises(raises):
            with Image.open(f):
                pass


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/timeout-1ee28a249896e05b83840ae8140622de8e648ba9.psd",
        "Tests/images/timeout-598843abc37fc080ec36a2699ebbd44f795d3a6f.psd",
    ],
)
def test_layer_crashes(test_file: str) -> None:
    with open(test_file, "rb") as f:
        with Image.open(f) as im:
            assert isinstance(im, PsdImagePlugin.PsdImageFile)
            with pytest.raises(SyntaxError):
                im.layers
