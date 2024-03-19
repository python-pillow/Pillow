from __future__ import annotations

import pytest

from PIL import Image

from .helper import (
    assert_image_equal,
    skip_unless_feature,
)

pytestmark = [
    skip_unless_feature("jpegxl"),
]


def test_n_frames() -> None:
    """Ensure that jxl format sets n_frames and is_animated attributes correctly."""

    with Image.open("Tests/images/hopper.jxl") as im:
        assert im.n_frames == 1
        assert not im.is_animated

    with Image.open("Tests/images/iss634.jxl") as im:
        assert im.n_frames == 41
        assert im.is_animated


def test_float_duration() -> None:

    with Image.open("Tests/images/iss634.jxl") as im:
        im.load()
        assert im.info["duration"] == 70


def test_seeking() -> None:
    """
    Open an animated jxl file, and then try seeking through frames in reverse-order,
    verifying the durations are correct.
    """

    with Image.open("Tests/images/jxl/traffic_light.jxl") as im1:
        with Image.open("Tests/images/jxl/traffic_light.gif") as im2:
            assert im1.n_frames == im2.n_frames
            assert im1.is_animated

            # Traverse frames in reverse, checking timestamps and durations
            total_dur = 0
            for frame in reversed(range(im1.n_frames)):
                im1.seek(frame)
                im1.load()
                im2.seek(frame)
                im2.load()

                assert_image_equal(im1.convert("RGB"), im2.convert("RGB"))

                total_dur += im1.info["duration"]
                assert im1.info["duration"] == im2.info["duration"]
                assert im1.info["timestamp"] == im1.info["timestamp"]
            assert total_dur == 8000

            assert im1.tell() == 0 and im2.tell() == 0

            im1.seek(0)
            im1.load()
            im2.seek(0)
            im2.load()


def test_seek_errors() -> None:
    with Image.open("Tests/images/iss634.jxl") as im:
        with pytest.raises(EOFError):
            im.seek(-1)

        with pytest.raises(EOFError):
            im.seek(47)
