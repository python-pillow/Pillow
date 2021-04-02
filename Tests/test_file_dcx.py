import pytest

from PIL import DcxImagePlugin, Image

from .helper import assert_image_equal, hopper, is_pypy

# Created with ImageMagick: convert hopper.ppm hopper.dcx
TEST_FILE = "Tests/images/hopper.dcx"


def test_sanity():
    # Arrange

    # Act
    with Image.open(TEST_FILE) as im:

        # Assert
        assert im.size == (128, 128)
        assert isinstance(im, DcxImagePlugin.DcxImageFile)
        orig = hopper()
        assert_image_equal(im, orig)


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file():
    def open():
        im = Image.open(TEST_FILE)
        im.load()

    pytest.warns(ResourceWarning, open)


def test_closed_file():
    with pytest.warns(None) as record:
        im = Image.open(TEST_FILE)
        im.load()
        im.close()

    assert not record


def test_context_manager():
    with pytest.warns(None) as record:
        with Image.open(TEST_FILE) as im:
            im.load()

    assert not record


def test_invalid_file():
    with open("Tests/images/flower.jpg", "rb") as fp:
        with pytest.raises(SyntaxError):
            DcxImagePlugin.DcxImageFile(fp)


def test_tell():
    # Arrange
    with Image.open(TEST_FILE) as im:

        # Act
        frame = im.tell()

        # Assert
        assert frame == 0


def test_n_frames():
    with Image.open(TEST_FILE) as im:
        assert im.n_frames == 1
        assert not im.is_animated


def test_eoferror():
    with Image.open(TEST_FILE) as im:
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_seek_too_far():
    # Arrange
    with Image.open(TEST_FILE) as im:
        frame = 999  # too big on purpose

    # Act / Assert
    with pytest.raises(EOFError):
        im.seek(frame)
