#!/usr/bin/env python3
from __future__ import annotations

import sys

from PIL import Image

if sys.maxsize < 2**32:
    im = Image.new("L", (999999, 999999), 0)
