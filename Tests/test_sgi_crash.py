#!/usr/bin/env python
import pytest
from PIL import Image


def test_crashes():
    with open("Tests/images/sgi_crash.bin", "rb") as f:
        im = Image.open(f)
        with pytest.raises(IOError):
            im.load()


def test_overrun_crashes():
    with open("Tests/images/sgi_overrun_expandrowF04.bin", "rb") as f:
        im = Image.open(f)
        with pytest.raises(IOError):
            im.load()
