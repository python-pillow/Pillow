#!/bin/bash

set -e

python3 -c "from PIL import Image"

python3 -bb -m pytest -vv -x -W always Tests -m "isolated"
python3 -bb -m pytest -vv -x -W always Tests -m "not isolated" \
  --numprocesses=logical --dist=worksteal \
  --cov PIL --cov Tests --cov-report term --cov-report xml
