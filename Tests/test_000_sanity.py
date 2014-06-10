from __future__ import print_function
from tester import *

import PIL
import PIL.Image

# Make sure we have the binary extension
im = PIL.Image.core.new("L", (100, 100))

assert PIL.Image.VERSION[:3] == '1.1'

# Create an image and do stuff with it.
im = PIL.Image.new("1", (100, 100))
assert (im.mode, im.size) == ('1', (100, 100))
assert len(im.tobytes()) == 1300

# Create images in all remaining major modes.
im = PIL.Image.new("L", (100, 100))
im = PIL.Image.new("P", (100, 100))
im = PIL.Image.new("RGB", (100, 100))
im = PIL.Image.new("I", (100, 100))
im = PIL.Image.new("F", (100, 100))

print("ok")
