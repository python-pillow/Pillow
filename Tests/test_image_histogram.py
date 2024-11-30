from __future__ import annotations

from .helper import hopper


def test_histogram() -> None:
    def histogram(mode: str) -> tuple[int, int, int]:
        h = hopper(mode).histogram()
        return len(h), min(h), max(h)

    assert histogram("1") == (256, 0, 10994)
    assert histogram("L") == (256, 0, 662)
    assert histogram("I") == (256, 0, 662)
    assert histogram("F") == (256, 0, 662)
    assert histogram("P") == (256, 0, 1551)
    assert histogram("RGB") == (768, 4, 675)
    assert histogram("RGBA") == (1024, 0, 16384)
    assert histogram("CMYK") == (1024, 0, 16384)
    assert histogram("YCbCr") == (768, 0, 1908)
