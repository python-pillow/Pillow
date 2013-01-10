from tester import *

from PIL import Image
try:
    from PIL import ImageGL
except ImportError as v:
    skip(v)

success()
