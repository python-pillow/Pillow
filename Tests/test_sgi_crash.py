#!/usr/bin/env python
import pytest

from PIL import Image


@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/sgi_overrun_expandrowF04.bin",
        "Tests/images/sgi_crash.bin",
        "Tests/images/crash-6b7f2244da6d0ae297ee0754a424213444e92778.sgi",
        "Tests/images/ossfuzz-5730089102868480.sgi",
    ],
)
def test_crashes(test_file):
    with open(test_file, "rb") as f:
        im = Image.open(f)
        with pytest.raises(OSError):
            im.load()
