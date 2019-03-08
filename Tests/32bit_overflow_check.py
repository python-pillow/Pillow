#!/usr/bin/env python

from PIL import Image
import sys


if sys.maxsize < 2**32:
    Image.core.set_blocks_max(2**29)
