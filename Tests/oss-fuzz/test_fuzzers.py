import subprocess
import sys

import fuzzers
import pytest

from PIL import Image

if sys.platform.startswith("win32"):
    pytest.skip("Fuzzer is linux only", allow_module_level=True)


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
    except (
        OSError,
        SyntaxError,
        MemoryError,
        ValueError,
        NotImplementedError,
        OverflowError,
    ):
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
    if not path:
        return
    with open(path, "rb") as f:
        try:
            fuzzers.fuzz_font(f.read())
        except (Image.DecompressionBombError, Image.DecompressionBombWarning):
            pass
        assert True
