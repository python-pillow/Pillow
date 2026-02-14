from __future__ import annotations

from .helper import assert_image_equal, hopper


def check_upload_equal() -> None:
    result = hopper("P").convert("RGB")
    target = hopper("RGB")
    assert_image_equal(result, target)


def check_upload_similar() -> None:
    result = hopper("P").convert("RGB")
    target = hopper("RGB")
    assert_image_equal(result, target)
