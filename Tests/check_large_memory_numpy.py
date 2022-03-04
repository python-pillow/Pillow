import sys

import pytest

from PIL import Image

# This test is not run automatically.
#
# It requires > 2gb memory for the >2 gigapixel image generated in the
# second test.  Running this automatically would amount to a denial of
# service on our testing infrastructure.  I expect this test to fail
# on any 32-bit machine, as well as any smallish things (like
# Raspberry Pis).


np = pytest.importorskip("numpy", reason="NumPy not installed")

YDIM = 32769
XDIM = 48000


pytestmark = pytest.mark.skipif(sys.maxsize <= 2 ** 32, reason="requires 64-bit system")


def _write_png(tmp_path, xdim, ydim):
    dtype = np.uint8
    a = np.zeros((xdim, ydim), dtype=dtype)
    f = str(tmp_path / "temp.png")
    im = Image.fromarray(a, "L")
    im.save(f)


def test_large(tmp_path):
    """succeeded prepatch"""
    _write_png(tmp_path, XDIM, YDIM)


def test_2gpx(tmp_path):
    """failed prepatch"""
    _write_png(tmp_path, XDIM, XDIM)
