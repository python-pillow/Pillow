#!/bin/bash

set -e

python3 -c "from PIL import Image"

python3 -bb -m pytest -v -x -W always --cov PIL --cov Tests --cov-report term Tests $REVERSE
