from __future__ import annotations

import pytest

from .helper import hopper


def test_sanity() -> None:
    im = hopper()

    type_repr = repr(type(im.getim()))
    assert "PyCapsule" in type_repr

    with pytest.warns(DeprecationWarning, match="id property"):
        assert isinstance(im.im.id, int)

    with pytest.warns(DeprecationWarning, match="unsafe_ptrs property"):
        ptrs = dict(im.im.unsafe_ptrs)
    assert ptrs.keys() == {"image8", "image32", "image"}
