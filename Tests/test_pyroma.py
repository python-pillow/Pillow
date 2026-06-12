from __future__ import annotations

import subprocess
import sys

import pytest

pytest.importorskip("pyroma", reason="Pyroma not installed")


@pytest.mark.skipif(sys.platform == "ios", reason="Processes not supported on iOS")
def test_pyroma() -> None:
    assert b"Final rating: 10/10" in subprocess.check_output(
        [sys.executable, "-m", "pyroma", "."]
    )
