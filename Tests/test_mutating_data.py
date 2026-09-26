from __future__ import annotations

from typing import Any

import pytest

from PIL import Image, ImageFilter


class MutatingFloat:
    def __init__(self, seq: list[Any]) -> None:
        self.seq = seq

    def __float__(self) -> float:
        self.seq.clear()
        return 1.0


class MutatingIndex:
    def __init__(self, seq: list[Any]) -> None:
        self.seq = seq

    def __index__(self) -> int:
        self.seq.clear()
        return 0


def test_kernel_mutate_during_iteration() -> None:
    # Test `getlist()` behaves correctly when the sequence is mutated during iteration.
    # `ImageFilter.Kernel()` is one of the users of `getlist()`.
    kernel: list[Any] = []

    kernel[:] = [MutatingFloat(kernel), *range(8)]
    im = Image.new("L", (8, 8))
    with pytest.raises(RuntimeError, match="changed size during iteration"):
        im.filter(ImageFilter.Kernel((3, 3), kernel, scale=1))


@pytest.mark.parametrize("mode", ("L", "F", "I", "I;16"))
def test_putdata_mutate_during_iteration(mode: str) -> None:
    # An element whose coercion mutates the source sequence must not corrupt memory.
    data: list[Any] = []
    data[:] = [MutatingFloat(data)] + [0.0] * 15
    im = Image.new(mode, (4, 4))
    with pytest.raises(RuntimeError, match="changed size during iteration"):
        im.putdata(data)


def test_putdata_getink_mutate_during_iteration() -> None:
    # RGB pixels go through getink(), which coerces the first channel via __index__.
    # That too must not read a freed sequence.
    rgb_data: list[Any] = []
    rgb_data[:] = [(MutatingIndex(rgb_data), 0, 0)] + [(0, 0, 0)] * 15
    im = Image.new("RGB", (4, 4))
    with pytest.raises(RuntimeError, match="changed size during iteration"):
        im.putdata(rgb_data)
