from __future__ import annotations

import subprocess
import sys

import fuzzers
import packaging
import pytest

from PIL import Image, UnidentifiedImageError, features
from Tests.helper import skip_unless_feature

if sys.platform.startswith("win32"):
    pytest.skip("Fuzzer is linux only", allow_module_level=True)
libjpeg_turbo_version = features.version("libjpeg_turbo")
if libjpeg_turbo_version is not None:
    version = packaging.version.parse(libjpeg_turbo_version)
    if version.major == 2 and version.minor == 0:
        pytestmark = pytest.mark.valgrind_known_error(
            reason="Known failing with libjpeg_turbo 2.0"
        )


@pytest.mark.parametrize(
    "path",
    subprocess.check_output("find Tests/images -type f", shell=True).split(b"\n"),
)
def test_fuzz_images(path: str) -> None:
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
        UnidentifiedImageError,
    ):
        # Known Image.* exceptions
        assert True
    finally:
        fuzzers.disable_decompressionbomb_error()


@skip_unless_feature("freetype2")
@pytest.mark.parametrize(
    "path", subprocess.check_output("find Tests/fonts -type f", shell=True).split(b"\n")
)
def test_fuzz_fonts(path: str) -> None:
    if not path:
        return
    with open(path, "rb") as f:
        try:
            fuzzers.fuzz_font(f.read())
        except (Image.DecompressionBombError, Image.DecompressionBombWarning, OSError):
            pass
        assert True
