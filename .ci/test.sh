#!/bin/bash

set -e

python -bb -m pytest -v -x -W always --cov PIL --cov Tests --cov-report term Tests
