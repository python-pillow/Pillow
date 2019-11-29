import unittest
from io import BytesIO

from PIL import Image, features

from .helper import PillowLeakTestCase

test_file = "Tests/images/hopper.webp"


@unittest.skipUnless(features.check("webp"), "WebP is not installed")
class TestWebPLeaks(PillowLeakTestCase):

    mem_limit = 3 * 1024  # kb
    iterations = 100

    def test_leak_load(self):
        with open(test_file, "rb") as f:
            im_data = f.read()

        def core():
            with Image.open(BytesIO(im_data)) as im:
                im.load()

        self._test_leak(core)
