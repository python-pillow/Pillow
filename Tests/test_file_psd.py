import pytest

from PIL import Image, PsdImagePlugin

from .helper import assert_image_similar, hopper, is_pypy

test_file = "Tests/images/hopper.psd"


def test_sanity():
    with Image.open(test_file) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "PSD"
        assert im.get_format_mimetype() == "image/vnd.adobe.photoshop"

        im2 = hopper()
        assert_image_similar(im, im2, 4.8)


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file():
    def open():
        im = Image.open(test_file)
        im.load()

    pytest.warns(ResourceWarning, open)


def test_closed_file():
    with pytest.warns(None) as record:
        im = Image.open(test_file)
        im.load()
        im.close()

    assert not record


def test_context_manager():
    with pytest.warns(None) as record:
        with Image.open(test_file) as im:
            im.load()

    assert not record


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        PsdImagePlugin.PsdImageFile(invalid_file)


def test_n_frames():
    with Image.open("Tests/images/hopper_merged.psd") as im:
        assert im.n_frames == 1
        assert not im.is_animated

    for path in [test_file, "Tests/images/negative_layer_count.psd"]:
        with Image.open(path) as im:
            assert im.n_frames == 2
            assert im.is_animated


def test_eoferror():
    with Image.open(test_file) as im:
        # PSD seek index starts at 1 rather than 0
        n_frames = im.n_frames + 1

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_seek_tell():
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


def test_seek_eoferror():
    with Image.open(test_file) as im:

        with pytest.raises(EOFError):
            im.seek(-1)


def test_open_after_exclusive_load():
    with Image.open(test_file) as im:
        im.load()
        im.seek(im.tell() + 1)
        im.load()


def test_icc_profile():
    with Image.open(test_file) as im:
        assert "icc_profile" in im.info

        icc_profile = im.info["icc_profile"]
        assert len(icc_profile) == 3144


def test_no_icc_profile():
    with Image.open("Tests/images/hopper_merged.psd") as im:
        assert "icc_profile" not in im.info


def test_combined_larger_than_size():
    # The 'combined' sizes of the individual parts is larger than the
    # declared 'size' of the extra data field, resulting in a backwards seek.

    # If we instead take the 'size' of the extra data field as the source of truth,
    # then the seek can't be negative
    with pytest.raises(OSError):
        with Image.open("Tests/images/combined_larger_than_size.psd"):
            pass


@pytest.mark.parametrize(
    "test_file,raises",
    [
        (
            "Tests/images/timeout-1ee28a249896e05b83840ae8140622de8e648ba9.psd",
            Image.UnidentifiedImageError,
        ),
        (
            "Tests/images/timeout-598843abc37fc080ec36a2699ebbd44f795d3a6f.psd",
            Image.UnidentifiedImageError,
        ),
        ("Tests/images/timeout-c8efc3fded6426986ba867a399791bae544f59bc.psd", OSError),
        ("Tests/images/timeout-dedc7a4ebd856d79b4359bbcc79e8ef231ce38f6.psd", OSError),
    ],
)
def test_crashes(test_file, raises):
    with open(test_file, "rb") as f:
        with pytest.raises(raises):
            with Image.open(f):
                pass
