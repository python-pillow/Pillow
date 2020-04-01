#!/usr/bin/env python
from PIL import Image

from .helper import PillowTestCase

repro = (
    "Tests/images/sgi_overrun_expandrowF04.bin",
    "Tests/images/sgi_crash.bin",
)


class TestSgiCrashes(PillowTestCase):
    def test_crashes(self):
        for path in repro:
            with open(path, "rb") as f:
                im = Image.open(f)
                with self.assertRaises(IOError):
                    im.load()
