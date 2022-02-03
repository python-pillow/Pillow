import filecmp

import pytest

from PIL import Image, ImImagePlugin

from .helper import assert_image_equal_tofile, hopper, is_pypy

# sample im
TEST_IM = "Tests/images/hopper.im"


def test_sanity():
    with Image.open(TEST_IM) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format == "IM"


def test_name_limit(tmp_path):
    out = str(tmp_path / ("name_limit_test" * 7 + ".im"))
    with Image.open(TEST_IM) as im:
        im.save(out)
    assert filecmp.cmp(out, "Tests/images/hopper_long_name.im")


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file():
    def open():
        im = Image.open(TEST_IM)
        im.load()

    pytest.warns(ResourceWarning, open)


def test_closed_file():
    with pytest.warns(None) as record:
        im = Image.open(TEST_IM)
        im.load()
        im.close()

    assert not record


def test_context_manager():
    with pytest.warns(None) as record:
        with Image.open(TEST_IM) as im:
            im.load()

    assert not record


def test_tell():
    # Arrange
    with Image.open(TEST_IM) as im:

        # Act
        frame = im.tell()

    # Assert
    assert frame == 0


def test_n_frames():
    with Image.open(TEST_IM) as im:
        assert im.n_frames == 1
        assert not im.is_animated


def test_eoferror():
    with Image.open(TEST_IM) as im:
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_roundtrip(tmp_path):
    def roundtrip(mode):
        out = str(tmp_path / "temp.im")
        im = hopper(mode)
        im.save(out)
        assert_image_equal_tofile(im, out)

    for mode in ["RGB", "P", "PA"]:
        roundtrip(mode)


def test_save_unsupported_mode(tmp_path):
    out = str(tmp_path / "temp.im")
    im = hopper("HSV")
    with pytest.raises(ValueError):
        im.save(out)


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        ImImagePlugin.ImImageFile(invalid_file)


def test_number():
    assert ImImagePlugin.number("1.2") == 1.2
