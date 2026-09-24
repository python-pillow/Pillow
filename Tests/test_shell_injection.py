from __future__ import annotations

import shutil
from io import BytesIO

import pytest

from PIL import Image, JpegImagePlugin

from .helper import djpeg_available, is_win32

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from typing import IO

TEST_JPG = "Tests/images/hopper.jpg"

test_filenames = ("temp_';", 'temp_";', "temp_'\"|", "temp_'\"||", "temp_'\"&&")


@pytest.mark.skipif(is_win32(), reason="Requires Unix or macOS")
class TestShellInjection:
    def assert_save_filename_check(
        self,
        tmp_path: Path,
        src_img: Image.Image,
        save_func: Callable[[Image.Image, IO[bytes], str | bytes], None],
    ) -> None:
        for filename in test_filenames:
            dest_file = str(tmp_path / filename)
            save_func(src_img, BytesIO(), dest_file)
            # If file can't be opened, shell injection probably occurred
            with Image.open(dest_file) as im:
                im.load()

    @pytest.mark.skipif(not djpeg_available(), reason="djpeg not available")
    def test_load_djpeg_filename(self, tmp_path: Path) -> None:
        for filename in test_filenames:
            src_file = tmp_path / filename
            shutil.copy(TEST_JPG, src_file)

            with Image.open(src_file) as im:
                assert isinstance(im, JpegImagePlugin.JpegImageFile)
                with pytest.warns(DeprecationWarning, match="load_djpeg"):
                    im.load_djpeg()
