import pytest
from PIL import Image, TarIO

from .helper import is_pypy

codecs = dir(Image.core)

# Sample tar archive
TEST_TAR_FILE = "Tests/images/hopper.tar"


def setup_module():
    if "zip_decoder" not in codecs and "jpeg_decoder" not in codecs:
        pytest.skip("neither jpeg nor zip support available")


def test_sanity():
    for codec, test_path, format in [
        ["zip_decoder", "hopper.png", "PNG"],
        ["jpeg_decoder", "hopper.jpg", "JPEG"],
    ]:
        if codec in codecs:
            with TarIO.TarIO(TEST_TAR_FILE, test_path) as tar:
                with Image.open(tar) as im:
                    im.load()
                    assert im.mode == "RGB"
                    assert im.size == (128, 128)
                    assert im.format == format


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file():
    def open():
        TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")

    pytest.warns(ResourceWarning, open)


def test_close():
    def open():
        tar = TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg")
        tar.close()

    pytest.warns(None, open)


def test_contextmanager():
    def open():
        with TarIO.TarIO(TEST_TAR_FILE, "hopper.jpg"):
            pass

    pytest.warns(None, open)
