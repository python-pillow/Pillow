from __future__ import annotations

import sys
from pathlib import Path

import fuzzers
import packaging
import pytest

from PIL import Image, features
from Tests.helper import skip_unless_feature

if sys.platform.startswith("win32") or sys.platform == "ios":
    pytest.skip("Fuzzer doesn't run on Windows or iOS", allow_module_level=True)

libjpeg_turbo_version = features.version("libjpeg_turbo")
if libjpeg_turbo_version is not None:
    version = packaging.version.parse(libjpeg_turbo_version)
    if version.major == 2 and version.minor == 0:
        pytestmark = pytest.mark.valgrind_known_error(
            reason="Known failing with libjpeg_turbo 2.0"
        )

tests_path = Path(__file__).parent.parent


def find_files(subdir: str) -> list[Path]:
    return [path for path in tests_path.joinpath(subdir).rglob("*") if path.is_file()]


@pytest.mark.parametrize(
    "path",
    find_files("images"),
    ids=lambda p: str(p.relative_to(tests_path)),
)
def test_fuzz_images(path: Path) -> None:
    fuzzers.enable_decompressionbomb_error()
    try:
        fuzzers.fuzz_image(path.read_bytes())
    except (
        # Known exceptions from Pillow
        OSError,
        SyntaxError,
        MemoryError,
        ValueError,
        NotImplementedError,
        OverflowError,
        # Known Image.* exceptions
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ):
        pass
    finally:
        fuzzers.disable_decompressionbomb_error()


@skip_unless_feature("freetype2")
@pytest.mark.parametrize(
    "path",
    find_files("fonts"),
    ids=lambda p: str(p.relative_to(tests_path)),
)
def test_fuzz_fonts(path: Path) -> None:
    try:
        fuzzers.fuzz_font(path.read_bytes())
    except (Image.DecompressionBombError, Image.DecompressionBombWarning, OSError):
        pass
