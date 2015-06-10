#!/usr/bin/env python

from PIL import Image
import sys


if sys.maxsize < 2**32:
    im = Image.new('L', (999999, 999999), 0)
