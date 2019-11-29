#!/usr/bin/env python3

import glob
import os
import subprocess
import sys

from config import VIRT_BASE, X64_EXT, pythons


def test_one(params):
    python, architecture = params
    try:
        print("Running: %s, %s" % params)
        command = [
            r"{}\{}{}\Scripts\python.exe".format(VIRT_BASE, python, architecture),
            "test-installed.py",
            "--processes=-0",
            "--process-timeout=30",
        ]
        command.extend(glob.glob("Tests/test*.py"))
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        (trace, stderr) = proc.communicate()
        status = proc.returncode
        print("Done with {}, {} -- {}".format(python, architecture, status))
        return (python, architecture, status, trace)
    except Exception as msg:
        print("Error with {}, {}: {}".format(python, architecture, msg))
        return (python, architecture, -1, str(msg))


if __name__ == "__main__":

    os.chdir("..")
    matrix = [
        (python, architecture) for python in pythons for architecture in ("", X64_EXT)
    ]

    results = map(test_one, matrix)

    for (python, architecture, status, trace) in results:
        print("{}{}: {}".format(python, architecture, status and "ERR" or "PASS"))

    res = all(status for (python, architecture, status, trace) in results)
    sys.exit(res)
