from __future__ import annotations

from .helper import hopper


def test_sanity():
    data = hopper().tobytes()
    assert isinstance(data, bytes)
