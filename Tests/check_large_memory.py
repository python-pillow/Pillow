from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

import pytest

from PIL import Image

# This test is not run automatically.
#
# It requires > 2gb memory for the >2 gigapixel image generated in the
# second test.  Running this automatically would amount to a denial of
# service on our testing infrastructure.  I expect this test to fail
# on any 32-bit machine, as well as any smallish things (like
# Raspberry Pis). It does succeed on a 3gb Ubuntu 12.04x64 VM on Python
# 2.7 and 3.2.


numpy: ModuleType | None
try:
    import numpy
except ImportError:
    numpy = None

YDIM = 32769
XDIM = 48000


pytestmark = pytest.mark.skipif(sys.maxsize <= 2**32, reason="requires 64-bit system")


def _write_png(tmp_path: Path, xdim: int, ydim: int) -> None:
    f = tmp_path / "temp.png"
    im = Image.new("L", (xdim, ydim), 0)
    im.save(f)


def test_large(tmp_path: Path) -> None:
    """succeeded prepatch"""
    _write_png(tmp_path, XDIM, YDIM)


def test_2gpx(tmp_path: Path) -> None:
    """failed prepatch"""
    _write_png(tmp_path, XDIM, XDIM)


@pytest.mark.skipif(numpy is None, reason="Numpy is not installed")
def test_size_greater_than_int() -> None:
    assert numpy is not None
    arr = numpy.ndarray(shape=(16394, 16394))
    Image.fromarray(arr)
