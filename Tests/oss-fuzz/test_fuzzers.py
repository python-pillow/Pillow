import subprocess

import fuzzers
import pytest

from PIL import Image


@pytest.mark.parametrize(
    "path",
    subprocess.check_output("find Tests/images -type f", shell=True).split(b"\n"),
)
def test_fuzz_images(path):
    fuzzers.enable_decompressionbomb_error()
    try:
        with open(path, "rb") as f:
            fuzzers.fuzz_image(f.read())
            assert True
    except (OSError, SyntaxError, MemoryError, ValueError, NotImplementedError):
        # Known exceptions that are through from Pillow
        assert True
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        Image.UnidentifiedImageError,
    ):
        # Known Image.* exceptions
        assert True


@pytest.mark.parametrize(
    "path", subprocess.check_output("find Tests/fonts -type f", shell=True).split(b"\n")
)
def test_fuzz_fonts(path):
    if not path or b"LICENSE.txt" in path or b".pil" in path:
        return
    with open(path, "rb") as f:
        fuzzers.fuzz_font(f.read())
        assert True
