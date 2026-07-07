from __future__ import annotations

from PIL import Image

TEST_FILE = "Tests/images/fli_overflow.fli"


def test_fli_overflow() -> None:
    # this should not crash with a malloc error or access violation
    with Image.open(TEST_FILE) as im:
        im.load()
