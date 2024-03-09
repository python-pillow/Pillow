from __future__ import annotations

from PIL import Image


def test_sanity() -> None:
    # Make sure we have the binary extension
    Image.core.new("L", (100, 100))

    # Create an image and do stuff with it.
    im = Image.new("1", (100, 100))
    assert (im.mode, im.size) == ("1", (100, 100))
    assert len(im.tobytes()) == 1300

    # Create images in all remaining major modes.
    Image.new("L", (100, 100))
    Image.new("P", (100, 100))
    Image.new("RGB", (100, 100))
    Image.new("I", (100, 100))
    Image.new("F", (100, 100))
