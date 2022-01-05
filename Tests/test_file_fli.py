import pytest

from PIL import FliImagePlugin, Image

from .helper import assert_image_equal_tofile, is_pypy

# created as an export of a palette image from Gimp2.6
# save as...-> hopper.fli, default options.
static_test_file = "Tests/images/hopper.fli"

# From https://samples.libav.org/fli-flc/
animated_test_file = "Tests/images/a.fli"


def test_sanity():
    with Image.open(static_test_file) as im:
        im.load()
        assert im.mode == "P"
        assert im.size == (128, 128)
        assert im.format == "FLI"
        assert not im.is_animated

    with Image.open(animated_test_file) as im:
        assert im.mode == "P"
        assert im.size == (320, 200)
        assert im.format == "FLI"
        assert im.info["duration"] == 71
        assert im.is_animated


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file():
    def open():
        im = Image.open(static_test_file)
        im.load()

    pytest.warns(ResourceWarning, open)


def test_closed_file():
    with pytest.warns(None) as record:
        im = Image.open(static_test_file)
        im.load()
        im.close()

    assert not record


def test_context_manager():
    with pytest.warns(None) as record:
        with Image.open(static_test_file) as im:
            im.load()

    assert not record


def test_tell():
    # Arrange
    with Image.open(static_test_file) as im:

        # Act
        frame = im.tell()

        # Assert
        assert frame == 0


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        FliImagePlugin.FliImageFile(invalid_file)


def test_n_frames():
    with Image.open(static_test_file) as im:
        assert im.n_frames == 1
        assert not im.is_animated

    with Image.open(animated_test_file) as im:
        assert im.n_frames == 384
        assert im.is_animated


def test_eoferror():
    with Image.open(animated_test_file) as im:
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_seek_tell():
    with Image.open(animated_test_file) as im:

        layer_number = im.tell()
        assert layer_number == 0

        im.seek(0)
        layer_number = im.tell()
        assert layer_number == 0

        im.seek(1)
        layer_number = im.tell()
        assert layer_number == 1

        im.seek(2)
        layer_number = im.tell()
        assert layer_number == 2

        im.seek(1)
        layer_number = im.tell()
        assert layer_number == 1


def test_seek():
    with Image.open(animated_test_file) as im:
        im.seek(50)

        assert_image_equal_tofile(im, "Tests/images/a_fli.png")


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/timeout-9139147ce93e20eb14088fe238e541443ffd64b3.fli",
        "Tests/images/timeout-bff0a9dc7243a8e6ede2408d2ffa6a9964698b87.fli",
    ],
)
@pytest.mark.timeout(timeout=3)
def test_timeouts(test_file):
    with open(test_file, "rb") as f:
        with Image.open(f) as im:
            with pytest.raises(OSError):
                im.load()


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/crash-5762152299364352.fli",
    ],
)
def test_crash(test_file):
    with open(test_file, "rb") as f:
        with Image.open(f) as im:
            with pytest.raises(OSError):
                im.load()
