from __future__ import annotations

from io import BytesIO

from PIL import Image

from .helper import PillowLeakTestCase, skip_unless_feature

test_file = "Tests/images/hopper.jxl"


@skip_unless_feature("jxl")
class TestJxlLeaks(PillowLeakTestCase):
    # TODO: lower the limit, I'm not sure what is correct limit since I have libjxl debug system-wide
    mem_limit = 16 * 1024  # kb
    iterations = 100

    def test_leak_load(self) -> None:
        with open(test_file, "rb") as f:
            im_data = f.read()

        def core() -> None:
            with Image.open(BytesIO(im_data)) as im:
                im.load()

        self._test_leak(core)
