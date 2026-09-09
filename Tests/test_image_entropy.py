from __future__ import annotations

import pytest

from .helper import hopper


def test_entropy() -> None:
    def entropy(mode: str) -> float:
        return hopper(mode).entropy()

    assert entropy("1") == pytest.approx(0.9138803254693582)
    assert entropy("L") == pytest.approx(7.063008716585465)
    assert entropy("I") == pytest.approx(7.063008716585465)
    assert entropy("F") == pytest.approx(7.063008716585465)
    assert entropy("P") == pytest.approx(5.082506854662517)
    assert entropy("RGB") == pytest.approx(8.821286587714319)
    assert entropy("RGBA") == pytest.approx(7.42724306524488)
    assert entropy("CMYK") == pytest.approx(7.4272430652448795)
    assert entropy("YCbCr") == pytest.approx(7.698360534903628)
