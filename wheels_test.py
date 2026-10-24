#!/usr/bin/env python3

from __future__ import annotations

import runpy
import sys


def run_module(mod_name, *args):
    old_args = sys.argv[1:]
    sys.argv[1:] = args
    try:
        runpy.run_module(mod_name, run_name="__main__", alter_sys=True)
    except SystemExit as e:
        if e.code not in [0, None]:
            raise
    finally:
        sys.argv[1:] = old_args


if __name__ == "__main__":
    run_module("selftest")

    pytest_args = ["pytest", "-vv", "-x"]
    run_module(*pytest_args, "checks/check_wheel.py")

    # Mobile platforms don't support multiple processes.
    if sys.platform not in ["android", "ios"]:
        pytest_args += ["--numprocesses=logical", "--dist=worksteal"]
    run_module(*pytest_args, "Tests")
