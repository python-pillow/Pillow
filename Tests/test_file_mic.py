import pytest

from PIL import Image, ImagePalette

from .helper import assert_image_similar, hopper, skip_unless_feature

MicImagePlugin = pytest.importorskip(
    "PIL.MicImagePlugin", reason="olefile not installed"
)
pytestmark = skip_unless_feature("libtiff")
TEST_FILE = "Tests/images/hopper.mic"


def test_sanity():
    with Image.open(TEST_FILE) as im:
        im.load()
        assert im.mode == "RGBA"
        assert im.size == (128, 128)
        assert im.format == "MIC"

        # Adjust for the gamma of 2.2 encoded into the file
        lut = ImagePalette.make_gamma_lut(1 / 2.2)
        im = Image.merge("RGBA", [chan.point(lut) for chan in im.split()])

        im2 = hopper("RGBA")
        assert_image_similar(im, im2, 10)


def test_n_frames():
    with Image.open(TEST_FILE) as im:
        assert im.n_frames == 1


def test_is_animated():
    with Image.open(TEST_FILE) as im:
        assert not im.is_animated


def test_tell():
    with Image.open(TEST_FILE) as im:
        assert im.tell() == 0


def test_seek():
    with Image.open(TEST_FILE) as im:
        im.seek(0)
        assert im.tell() == 0

        with pytest.raises(EOFError):
            im.seek(99)
        assert im.tell() == 0


def test_invalid_file():
    # Test an invalid OLE file
    invalid_file = "Tests/images/flower.jpg"
    with pytest.raises(SyntaxError):
        MicImagePlugin.MicImageFile(invalid_file)

    # Test a valid OLE file, but not a MIC file
    ole_file = "Tests/images/test-ole-file.doc"
    with pytest.raises(SyntaxError):
        MicImagePlugin.MicImageFile(ole_file)
