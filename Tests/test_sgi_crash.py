#!/usr/bin/env python
import pytest
from PIL import Image


@pytest.mark.parametrize(
    "test_file",
    ["Tests/images/sgi_overrun_expandrowF04.bin", "Tests/images/sgi_crash.bin"],
)
def test_crashes(test_file):
    with open(test_file, "rb") as f:
        im = Image.open(f)
        with pytest.raises(OSError):
            im.load()
