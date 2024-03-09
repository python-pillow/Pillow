from __future__ import annotations

import subprocess
import sys


def test_main() -> None:
    args = [sys.executable, "-m", "PIL.report"]
    out = subprocess.check_output(args).decode("utf-8")
    lines = out.splitlines()
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Pillow ")
    assert lines[2].startswith("Python ")
    lines = lines[3:]
    while lines[0].startswith("    "):
        lines = lines[1:]
    assert lines[0] == "-" * 68
    assert lines[1].startswith("Python executable is")
    lines = lines[2:]
    if lines[0].startswith("Environment Python files loaded from"):
        lines = lines[1:]
    assert lines[0].startswith("System Python files loaded from")
    assert lines[1] == "-" * 68
    assert lines[2].startswith("Python Pillow modules loaded from ")
    assert lines[3].startswith("Binary Pillow modules loaded from ")
    assert lines[4] == "-" * 68
    assert "JPEG image/jpeg" not in out
