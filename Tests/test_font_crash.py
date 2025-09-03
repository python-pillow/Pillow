from __future__ import annotations

import pytest

from .helper import skip_unless_feature
from .oss_fuzz.fuzzers import fuzz_font


class TestFontCrash:
    @skip_unless_feature("freetype2")
    def test_segfault(self) -> None:
        with open("Tests/fonts/fuzz_font-5203009437302784", "rb") as fp:
            with pytest.raises(OSError):
                fuzz_font(fp.read())
