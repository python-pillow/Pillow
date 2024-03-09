from __future__ import annotations

from .helper import hopper


def test_sanity() -> None:
    im = hopper()
    type_repr = repr(type(im.getim()))

    assert "PyCapsule" in type_repr
    assert isinstance(im.im.id, int)
