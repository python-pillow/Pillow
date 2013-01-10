from tester import *

from PIL import Image
try:
    from PIL import ImageQt
except ImportError as v:
    skip(v)

success()
