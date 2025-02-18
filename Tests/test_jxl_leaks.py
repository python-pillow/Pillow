from __future__ import annotations

from io import BytesIO

from PIL import Image

from .helper import PillowLeakTestCase, skip_unless_feature

TEST_FILE = "Tests/images/hopper.jxl"


@skip_unless_feature("jpegxl")
class TestJpegXlLeaks(PillowLeakTestCase):
    mem_limit = 6 * 1024  # kb
    iterations = 1000

    def test_leak_load(self) -> None:
        with open(TEST_FILE, "rb") as f:
            im_data = f.read()

        def core() -> None:
            with Image.open(BytesIO(im_data)) as im:
                im.load()

        self._test_leak(core)
