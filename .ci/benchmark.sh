#!/bin/bash

set -e

python3 -m pip install pytest-benchmark

python3 -bb -m pytest -vv --benchmark-only --benchmark-autosave Tests/benchmark*
